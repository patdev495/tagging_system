from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from src.core import models
from typing import Optional, cast as typing_cast
import datetime
from sqlalchemy import cast, Date, func, case

def get_cartons(
    db: Session, 
    skip: int = 0, 
    limit: int = 50, 
    search: Optional[str] = None,
    product_id: Optional[int] = None,
    status: Optional[str] = None
):
    # Subquery to get the latest (max) ID for each unique carton_sn
    max_id_sub = db.query(
        func.max(models.Carton.id).label("max_id")
    ).group_by(models.Carton.carton_sn).subquery()

    # Subquery to count the total print attempts for each unique carton_sn
    count_sub = db.query(
        models.Carton.carton_sn.label("carton_sn"),
        func.count(models.Carton.id).label("print_count")
    ).group_by(models.Carton.carton_sn).subquery()

    # Base query joining the latest carton record with its count
    base_query = db.query(models.Carton, count_sub.c.print_count).join(
        max_id_sub, models.Carton.id == max_id_sub.c.max_id
    ).outerjoin(
        count_sub, models.Carton.carton_sn == count_sub.c.carton_sn
    ).options(joinedload(models.Carton.product))
    
    if search:
        base_query = base_query.filter(models.Carton.carton_sn.like(f"%{search}%"))
    if product_id:
        base_query = base_query.filter(models.Carton.product_id == product_id)
    if status:
        base_query = base_query.filter(models.Carton.status == status)
        
    total = base_query.count()
    results = base_query.order_by(models.Carton.id.desc()).offset(skip).limit(limit).all()
    
    items = []
    for carton, print_count in results:
        carton.reprint_count = max((print_count or 1) - 1, 0)
        orig_id = db.query(models.Carton.id).filter(
            models.Carton.carton_sn == carton.carton_sn,
            models.Carton.is_reprint == 0
        ).scalar()
        carton.items_count = db.query(models.CartonItem).filter(models.CartonItem.carton_id == (orig_id or carton.id)).count()
        items.append(carton)
        
    return {"total": total, "items": items}

def get_carton_detail(db: Session, carton_id: int):
    carton = db.query(models.Carton).options(
        joinedload(models.Carton.product),
        joinedload(models.Carton.items)
    ).filter(models.Carton.id == carton_id).first()
    
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
        
    # If this is a reprint, resolve items from the original carton
    if typing_cast(int, carton.is_reprint) == 1:
        original_carton = db.query(models.Carton).options(
            joinedload(models.Carton.items)
        ).filter(
            models.Carton.carton_sn == carton.carton_sn,
            models.Carton.is_reprint == 0
        ).first()
        items = original_carton.items if original_carton else []
        carton.items = items
    else:
        items = carton.items

    carton.items_count = len(typing_cast(list, items))
    
    # Query all other print attempts for this carton_sn as history
    print_history = db.query(models.Carton).filter(
        models.Carton.carton_sn == carton.carton_sn,
        models.Carton.id != carton.id
    ).order_by(models.Carton.id.asc()).all()
    
    orig_carton_id = db.query(models.Carton.id).filter(
        models.Carton.carton_sn == carton.carton_sn,
        models.Carton.is_reprint == 0
    ).scalar()
    orig_item_count = db.query(models.CartonItem).filter(models.CartonItem.carton_id == orig_carton_id).count() if orig_carton_id else 0
    
    for h in print_history:
        h.items_count = orig_item_count
        h.reprint_count = 0  # Not applicable for history items
        
    carton.print_history = print_history
    carton.reprint_count = len(print_history)
    
    return carton

def search_carton_by_sn(carton_sn: str, db: Session):
    carton = db.query(models.Carton).filter(models.Carton.carton_sn == carton_sn).order_by(models.Carton.id.desc()).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    
    return get_carton_detail(db, typing_cast(int, carton.id))

def search_by_item_sn(item_sn: str, db: Session):
    # Find the item first
    item = db.query(models.CartonItem).filter(models.CartonItem.item_sn == item_sn).order_by(models.CartonItem.id.desc()).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item S/N not found in any carton")
    
    # Return the associated carton with details
    return get_carton_detail(db, typing_cast(int, item.carton_id))

def delete_carton(db: Session, carton_id: int):
    carton = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    
    slot = db.query(models.JobOrderCartonSlot).filter(
        models.JobOrderCartonSlot.carton_id == carton_id
    ).first()
    if slot:
        slot.status = "PENDING"
        slot.scanned_at = None
        slot.carton_id = None

    # Delete associated items first (if no cascade delete in models)
    db.query(models.CartonItem).filter(models.CartonItem.carton_id == carton_id).delete()
    
    # Delete the carton
    db.delete(carton)
    db.commit()
    return {"message": "Carton deleted successfully"}

def get_packaging_statistics(db: Session, start_date: str, end_date: str):
    # Parse dates
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date + " 23:59:59.999", "%Y-%m-%d %H:%M:%S.%f")
    
    # 1. Summary Metrics
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
    
    # 2. Daily Breakdown
    # MSSQL/SQLite compatible grouping
    daily_results = db.query(
        cast(models.Carton.created_at, Date).label("date"),
        func.count(models.Carton.id).label("total"),
        func.sum(case((models.Carton.status == "SUCCESS", 1), else_=0)).label("success"),
        func.sum(case((models.Carton.is_reprint == 1, 1), else_=0)).label("reprint")
    ).filter(
        models.Carton.created_at >= start_dt,
        models.Carton.created_at <= end_dt
    ).group_by(
        cast(models.Carton.created_at, Date)
    ).order_by(
        cast(models.Carton.created_at, Date)
    ).all()
    
    daily_breakdown = []
    for r in daily_results:
        daily_breakdown.append({
            "date": str(r.date),
            "total": int(r.total or 0),
            "success": int(r.success or 0),
            "reprint": int(r.reprint or 0)
        })
        
    # 3. Product Breakdown
    product_results = db.query(
        models.Product.item_name.label("item_name"),
        func.count(models.Carton.id).label("total"),
        func.sum(case((models.Carton.is_reprint == 1, 1), else_=0)).label("reprint")
    ).join(
        models.Carton, models.Carton.product_id == models.Product.id
    ).filter(
        models.Carton.created_at >= start_dt,
        models.Carton.created_at <= end_dt
    ).group_by(
        models.Product.item_name
    ).order_by(
        func.count(models.Carton.id).desc()
    ).all()
    
    product_breakdown = []
    for r in product_results:
        product_breakdown.append({
            "item_name": str(r.item_name),
            "total": int(r.total or 0),
            "reprint": int(r.reprint or 0)
        })
        
    return {
        "total_cartons": total_cartons,
        "success_cartons": success_cartons,
        "failed_cartons": failed_cartons,
        "reprint_cartons": reprint_cartons,
        "total_items": total_items,
        "daily_breakdown": daily_breakdown,
        "product_breakdown": product_breakdown
    }


def get_job_order_statistics(db: Session, job_order: str):
    # 1. Total attempts and reprint attempts under this job_order
    total_attempts = db.query(models.Carton).filter(
        models.Carton.job_order == job_order
    ).count()

    reprint_attempts = db.query(models.Carton).filter(
        models.Carton.job_order == job_order,
        models.Carton.is_reprint == 1
    ).count()

    # 2. Get the latest print attempt per carton_sn in this job_order
    max_id_sub = db.query(
        func.max(models.Carton.id).label("max_id")
    ).filter(
        models.Carton.job_order == job_order
    ).group_by(models.Carton.carton_sn).subquery()

    count_sub = db.query(
        models.Carton.carton_sn.label("carton_sn"),
        func.count(models.Carton.id).label("print_count")
    ).filter(
        models.Carton.job_order == job_order
    ).group_by(models.Carton.carton_sn).subquery()

    results = db.query(models.Carton, count_sub.c.print_count).join(
        max_id_sub, models.Carton.id == max_id_sub.c.max_id
    ).outerjoin(
        count_sub, models.Carton.carton_sn == count_sub.c.carton_sn
    ).options(joinedload(models.Carton.product)).all()

    items = []
    success_count = 0
    failed_count = 0
    total_items = 0
    product_stats = {}

    for carton, print_count in results:
        # Populate carton properties
        orig_id = db.query(models.Carton.id).filter(
            models.Carton.carton_sn == carton.carton_sn,
            models.Carton.is_reprint == 0
        ).scalar()
        item_count = db.query(models.CartonItem).filter(models.CartonItem.carton_id == (orig_id or carton.id)).count()
        carton.items_count = item_count
        carton.reprint_count = max((print_count or 1) - 1, 0)
        items.append(carton)

        # Count total items
        total_items += item_count

        # Count success vs failed
        if carton.status == "SUCCESS":
            success_count += 1
        else:
            failed_count += 1

        # Product breakdown
        prod = carton.product
        if prod:
            prod_id = typing_cast(int, prod.id)
            if prod_id not in product_stats:
                product_stats[prod_id] = {
                    "product_id": prod_id,
                    "item_name": str(prod.item_name),
                    "total_cartons": 0,
                    "success_cartons": 0,
                    "failed_cartons": 0
                }
            product_stats[prod_id]["total_cartons"] += 1
            if carton.status == "SUCCESS":
                product_stats[prod_id]["success_cartons"] += 1
            else:
                product_stats[prod_id]["failed_cartons"] += 1

    return {
        "job_order": job_order,
        "total_cartons": len(items),
        "success_cartons": success_count,
        "failed_cartons": failed_count,
        "total_attempts": total_attempts,
        "reprint_attempts": reprint_attempts,
        "total_items": total_items,
        "product_breakdown": list(product_stats.values()),
        "cartons": items
    }
