import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc

from src.core import models
from .schemas import JobOrderSummary, JobOrderSlotDetail, POLotRunSummary

logger = logging.getLogger("ProductionRunService")

def get_job_orders_summary(db: Session) -> List[JobOrderSummary]:
    results = db.query(
        models.JobOrderCartonSlot.job_order,
        models.JobOrderCartonSlot.product_id,
        models.Product.item_name,
        models.Customer.code,
        func.count(models.JobOrderCartonSlot.id).label("total_slots"),
        func.sum(case((models.JobOrderCartonSlot.status == "SCANNED", 1), else_=0)).label("scanned_slots"),
        func.sum(case((models.JobOrderCartonSlot.status == "PENDING", 1), else_=0)).label("pending_slots"),
        func.sum(case((models.JobOrderCartonSlot.shipped == 1, 1), else_=0)).label("shipped_slots"),
        func.max(models.JobOrderCartonSlot.scanned_at).label("latest_scan_at")
    ).join(
        models.Product, models.JobOrderCartonSlot.product_id == models.Product.id
    ).outerjoin(
        models.Customer, models.Product.customer_id == models.Customer.id
    ).group_by(
        models.JobOrderCartonSlot.job_order,
        models.JobOrderCartonSlot.product_id,
        models.Product.item_name,
        models.Customer.code
    ).order_by(
        desc("latest_scan_at"),
        models.JobOrderCartonSlot.job_order.desc()
    ).all()

    summaries = []
    for r in results:
        total = r.total_slots or 0
        scanned = r.scanned_slots or 0
        pending = r.pending_slots or 0
        shipped = r.shipped_slots or 0
        comp_rate = round((scanned / total * 100), 1) if total > 0 else 0.0

        summaries.append(
            JobOrderSummary(
                job_order=r.job_order,
                product_id=r.product_id,
                product_name=r.item_name or "N/A",
                customer_code=r.code or "N/A",
                total_slots=total,
                scanned_slots=scanned,
                pending_slots=pending,
                shipped_slots=shipped,
                completion_rate=comp_rate,
                latest_scan_at=r.latest_scan_at
            )
        )
    return summaries

def get_job_order_slots(db: Session, job_order: str) -> List[JobOrderSlotDetail]:
    slots = db.query(models.JobOrderCartonSlot).filter(
        models.JobOrderCartonSlot.job_order == job_order
    ).order_by(models.JobOrderCartonSlot.carton_number.asc()).all()

    return [JobOrderSlotDetail.model_validate(s) for s in slots]

def get_po_lot_runs(db: Session) -> List[POLotRunSummary]:
    results = db.query(
        models.Carton.po_number,
        models.Carton.lot_number,
        models.Product.item_name,
        models.Customer.code,
        models.Carton.date_code,
        func.count(models.Carton.id).label("total_cartons"),
        func.sum(func.coalesce(models.Carton.weight, 0.0)).label("total_weight"),
        func.max(models.Carton.created_at).label("latest_packed_at")
    ).join(
        models.Product, models.Carton.product_id == models.Product.id
    ).outerjoin(
        models.Customer, models.Product.customer_id == models.Customer.id
    ).filter(
        models.Carton.po_number.isnot(None),
        models.Carton.po_number != ""
    ).group_by(
        models.Carton.po_number,
        models.Carton.lot_number,
        models.Product.item_name,
        models.Customer.code,
        models.Carton.date_code
    ).order_by(
        desc("latest_packed_at")
    ).all()

    runs = []
    for r in results:
        runs.append(
            POLotRunSummary(
                po_number=r.po_number or "N/A",
                lot_number=r.lot_number or "N/A",
                product_name=r.item_name or "N/A",
                customer_code=r.code or "N/A",
                date_code=r.date_code,
                total_cartons=r.total_cartons or 0,
                total_weight=round(float(r.total_weight or 0.0), 2),
                latest_packed_at=r.latest_packed_at
            )
        )
    return runs
