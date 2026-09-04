import datetime
import logging
from typing import List, Tuple, Dict
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, desc

from src.core import models
from .schemas import (
    DashboardStatsResponse,
    KPIStats,
    HourlyStat,
    ProductStat,
    LiveCartonFeed,
    SystemHealth,
)

logger = logging.getLogger("DashboardService")

def get_time_boundary(time_range: str) -> Tuple[datetime.datetime, datetime.datetime]:
    now = datetime.datetime.now()
    today_start = datetime.datetime.combine(now.date(), datetime.time.min)
    end_dt = datetime.datetime.combine(now.date(), datetime.time.max)

    if time_range == "7d":
        start_dt = today_start - datetime.timedelta(days=6)
    elif time_range == "30d":
        start_dt = today_start - datetime.timedelta(days=29)
    else:  # default "today"
        start_dt = today_start

    return start_dt, end_dt

def get_system_health() -> SystemHealth:
    try:
        from src.features.print.bartender_engine import bt_engine
        is_ready = bt_engine.is_initialized
        printers = bt_engine.get_printers()
        return SystemHealth(
            bartender_status="ready" if is_ready else "offline",
            active_printers_count=len(printers)
        )
    except Exception as e:
        logger.warning(f"Error checking system health: {e}")
        return SystemHealth(bartender_status="offline", active_printers_count=0)

def calculate_hourly_throughput(db: Session, start_dt: datetime.datetime, end_dt: datetime.datetime, time_range: str) -> List[HourlyStat]:
    cartons = db.query(models.Carton.created_at, models.Carton.status).filter(
        models.Carton.created_at >= start_dt,
        models.Carton.created_at <= end_dt
    ).all()

    if time_range == "today":
        # Default packaging shift hours: 06:00 to 22:00
        hour_keys = [f"{h:02d}:00" for h in range(6, 23)]
        # Add any cartons that fall outside 06:00-22:00
        extra_keys = set()
        for created_at, _ in cartons:
            if created_at:
                h_key = created_at.strftime("%H:00")
                if h_key not in hour_keys:
                    extra_keys.add(h_key)
        all_keys = sorted(list(set(hour_keys).union(extra_keys)))

        stats_map: Dict[str, Dict[str, int]] = {k: {"total": 0, "success": 0, "failed": 0} for k in all_keys}
        for created_at, status in cartons:
            if created_at:
                key = created_at.strftime("%H:00")
                if key in stats_map:
                    stats_map[key]["total"] += 1
                    if status == "SUCCESS":
                        stats_map[key]["success"] += 1
                    elif status == "FAILED":
                        stats_map[key]["failed"] += 1

        return [
            HourlyStat(
                hour=k,
                total=stats_map[k]["total"],
                success=stats_map[k]["success"],
                failed=stats_map[k]["failed"]
            )
            for k in all_keys
        ]
    else:
        # Multi-day: group by Date (DD/MM)
        days_count = 7 if time_range == "7d" else 30
        date_keys = []
        cur = start_dt.date()
        end_date = end_dt.date()
        while cur <= end_date:
            date_keys.append(cur.strftime("%d/%m"))
            cur += datetime.timedelta(days=1)

        stats_map = {k: {"total": 0, "success": 0, "failed": 0} for k in date_keys}
        for created_at, status in cartons:
            if created_at:
                key = created_at.strftime("%d/%m")
                if key in stats_map:
                    stats_map[key]["total"] += 1
                    if status == "SUCCESS":
                        stats_map[key]["success"] += 1
                    elif status == "FAILED":
                        stats_map[key]["failed"] += 1

        return [
            HourlyStat(
                hour=k,
                total=stats_map[k]["total"],
                success=stats_map[k]["success"],
                failed=stats_map[k]["failed"]
            )
            for k in date_keys
        ]

def calculate_top_products(db: Session, start_dt: datetime.datetime, end_dt: datetime.datetime, total_cartons: int) -> List[ProductStat]:
    results = db.query(
        models.Product.item_name,
        models.Customer.code,
        func.count(models.Carton.id).label("cnt")
    ).join(
        models.Carton, models.Carton.product_id == models.Product.id
    ).outerjoin(
        models.Customer, models.Product.customer_id == models.Customer.id
    ).filter(
        models.Carton.created_at >= start_dt,
        models.Carton.created_at <= end_dt
    ).group_by(
        models.Product.item_name,
        models.Customer.code
    ).order_by(
        desc("cnt")
    ).limit(8).all()

    top_products = []
    for item_name, customer_code, cnt in results:
        pct = round((cnt / total_cartons * 100), 1) if total_cartons > 0 else 0.0
        top_products.append(
            ProductStat(
                item_name=item_name or "Unknown",
                customer_code=customer_code or "N/A",
                count=cnt,
                percentage=pct
            )
        )
    return top_products

def get_dashboard_stats(db: Session, time_range: str = "today") -> DashboardStatsResponse:
    start_dt, end_dt = get_time_boundary(time_range)

    # 1. Query KPI counts
    total_cartons = db.query(models.Carton).filter(
        models.Carton.created_at >= start_dt,
        models.Carton.created_at <= end_dt
    ).count()

    success_cartons = db.query(models.Carton).filter(
        models.Carton.created_at >= start_dt,
        models.Carton.created_at <= end_dt,
        models.Carton.status == "SUCCESS"
    ).count()

    failed_cartons = db.query(models.Carton).filter(
        models.Carton.created_at >= start_dt,
        models.Carton.created_at <= end_dt,
        models.Carton.status == "FAILED"
    ).count()

    reprint_cartons = db.query(models.Carton).filter(
        models.Carton.created_at >= start_dt,
        models.Carton.created_at <= end_dt,
        models.Carton.is_reprint == 1
    ).count()

    total_items = db.query(models.CartonItem).join(
        models.Carton, models.CartonItem.carton_id == models.Carton.id
    ).filter(
        models.Carton.created_at >= start_dt,
        models.Carton.created_at <= end_dt
    ).count()

    success_rate = round((success_cartons / total_cartons * 100), 1) if total_cartons > 0 else 0.0
    error_rate = round((failed_cartons / total_cartons * 100), 1) if total_cartons > 0 else 0.0
    reprint_rate = round((reprint_cartons / total_cartons * 100), 1) if total_cartons > 0 else 0.0

    kpis = KPIStats(
        total_cartons=total_cartons,
        success_cartons=success_cartons,
        failed_cartons=failed_cartons,
        reprint_cartons=reprint_cartons,
        total_items=total_items,
        success_rate=success_rate,
        error_rate=error_rate,
        reprint_rate=reprint_rate
    )

    # 2. Hourly throughput
    hourly_throughput = calculate_hourly_throughput(db, start_dt, end_dt, time_range)

    # 3. Top products
    top_products = calculate_top_products(db, start_dt, end_dt, total_cartons)

    # 4. Live feed (Cycle 3)
    recent_cartons = db.query(models.Carton).options(
        joinedload(models.Carton.product).joinedload(models.Product.customer),
        selectinload(models.Carton.items)
    ).order_by(models.Carton.id.desc()).limit(15).all()

    live_feed: List[LiveCartonFeed] = []
    for c in recent_cartons:
        p_name = c.product.item_name if c.product else "N/A"
        c_code = c.product.customer.code if (c.product and c.product.customer) else "N/A"
        items_cnt = len(c.items) if c.items else 0
        live_feed.append(
            LiveCartonFeed(
                id=c.id,
                carton_sn=c.carton_sn or "N/A",
                item_name=p_name,
                customer_code=c_code,
                created_at=c.created_at or datetime.datetime.now(),
                status=c.status or "UNKNOWN",
                is_reprint=c.is_reprint or 0,
                weight=c.weight,
                station_id=c.station_id,
                items_count=items_cnt
            )
        )

    system = get_system_health()

    return DashboardStatsResponse(
        time_range=time_range,
        kpis=kpis,
        hourly_throughput=hourly_throughput,
        top_products=top_products,
        live_feed=live_feed,
        system=system
    )

