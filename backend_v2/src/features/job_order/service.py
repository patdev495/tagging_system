import math
import logging
from typing import cast
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from fastapi import HTTPException
from src.core import models
from src.features.carton.sn_allocator import plan_job_order_slots
from src.features.job_order import schemas

logger = logging.getLogger("JobOrderService")

def get_job_order_from_erp(db: Session, job_order: str):
    """
    Query the Job Order details from the Linked Server 192.168.206.18.
    If database engine is SQLite or if query fails due to database driver / connection issues,
    it falls back to a simulated mock response for local testing/development.
    """
    try:
        is_sqlite = db.get_bind().dialect.name == "sqlite"
    except Exception:
        is_sqlite = False
        
    if is_sqlite:
        logger.info(f"SQLite database detected. Falling back to mock for Job Order '{job_order}'")
        return get_mocked_job_order(db, job_order)

        
    query = text("""
        SELECT wadoco AS [工單], walitm AS [年益料號], wadl01 AS [客戶料號], wauorg/10000 AS [數量] 
        FROM [192.168.206.18].ShopFloorDW.DBO.F4801 
        WHERE wadoco = :job_order
    """)
    try:
        row = db.execute(query, {"job_order": job_order}).fetchone()
        if not row:
            raise HTTPException(status_code=400, detail=f"Không tìm thấy công lệnh '{job_order}' trên hệ thống ShopFloorDW.")
            
        wadoco = str(row[0]).strip()
        walitm = str(row[1]).strip()
        wadl01 = str(row[2]).strip()
        try:
            qty = int(row[3])
        except Exception:
            qty = 0
            
        return {
            "job_order": wadoco,
            "product_code": walitm,
            "customer_ref": wadl01,
            "quantity": qty
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Linked Server query failed: {e}. Raising HTTP error.")
        raise HTTPException(
            status_code=400, 
            detail=f"Không thể kết nối cơ sở dữ liệu ShopFloor hoặc công lệnh không hợp lệ. Chi tiết: {str(e)}"
        )

def get_mocked_job_order(db: Session, job_order: str):
    """
    Returns simulated Job Order details based on local products database.
    """
    product = db.query(models.Product).filter(models.Product.item_name == "UACC-Cable-Path-Outdoor-2M-BK").first()
    if not product:
        product = db.query(models.Product).first()
        
    if not product:
        return {
            "job_order": job_order,
            "product_code": "1CAD2420D2BK01NX9",
            "customer_ref": "UACC-Cable-Patch-Outdoor-2M-BK",
            "quantity": 750
        }
        
    ref_name = "UACC-Cable-Patch-Outdoor-2M-BK" if "Outdoor-2M-BK" in cast(str, product.item_name) else cast(str, product.item_name)
    return {
        "job_order": job_order,
        "product_code": "1CAD2420D2BK01NX9",
        "customer_ref": ref_name,
        "quantity": 15 * cast(int, product.packed_qty)
    }


def find_matching_product(db: Session, customer_ref: str, product_code: str):
    """
    Search for a Product matching either the Customer Ref (wadl01) or Product Code (walitm).
    Supports matching typos like Path vs Patch.
    """
    # 1. Match by item_name exactly
    product = db.query(models.Product).filter(models.Product.item_name == customer_ref).first()
    if product:
        return product
        
    # 2. Match by item_name case-insensitively
    product = db.query(models.Product).filter(func.lower(models.Product.item_name) == customer_ref.lower()).first()
    if product:
        return product
        
    # 3. Typo handling: Replace 'Patch' with 'Path' in the search ref
    if 'Patch' in customer_ref:
        path_ref = customer_ref.replace('Patch', 'Path')
        product = db.query(models.Product).filter(func.lower(models.Product.item_name) == path_ref.lower()).first()
        if product:
            return product
            
    # 4. Typo handling: Replace 'Path' with 'Patch' in the search ref
    if 'Path' in customer_ref:
        patch_ref = customer_ref.replace('Path', 'Patch')
        product = db.query(models.Product).filter(func.lower(models.Product.item_name) == patch_ref.lower()).first()
        if product:
            return product
            
    return None

def get_or_create_job_order_slots(db: Session, job_order: str):
    # 1. Fetch ERP Job Order details
    erp_data = get_job_order_from_erp(db, job_order)
    
    # 2. Find matching product
    product = find_matching_product(db, cast(str, erp_data["customer_ref"]), cast(str, erp_data["product_code"]))

    if not product:
        raise HTTPException(
            status_code=400, 
            detail=f"Không tìm thấy con hàng '{erp_data['customer_ref']}' tương ứng trong cơ sở dữ liệu."
        )
        
    # 3. Calculate total cartons
    packed_qty = cast(int, product.packed_qty)
    if packed_qty <= 0:
        raise HTTPException(status_code=400, detail=f"Sản phẩm '{product.item_name}' có packed_qty không hợp lệ ({packed_qty}).")
        
    total_qty = cast(int, erp_data["quantity"])
    total_cartons = math.ceil(total_qty / packed_qty)

    if total_cartons <= 0:
        raise HTTPException(status_code=400, detail=f"Số lượng sản phẩm trong công lệnh ({total_qty}) không đủ để đóng thùng.")
        
    # 4. Check if slots already exist
    existing_slots = db.query(models.JobOrderCartonSlot).filter(
        models.JobOrderCartonSlot.job_order == job_order
    ).order_by(models.JobOrderCartonSlot.carton_number).all()
    
    if existing_slots:
        return schemas.JobOrderDetailsResponse(
            job_order=job_order,
            total_qty=total_qty,
            total_cartons=total_cartons,
            product=schemas.JobOrderProductResponse.model_validate(product),
            slots=[schemas.JobOrderSlotResponse.model_validate(s) for s in existing_slots]
        )
        
    # 5. Allocate new slots
    sn_plans = plan_job_order_slots(db, product, total_cartons)
    slots = []
    for i, sn_plan in enumerate(sn_plans, start=1):
        slot = models.JobOrderCartonSlot(
            job_order=job_order,
            product_id=product.id,
            carton_number=i,
            carton_sn=sn_plan.carton_sn,
            status="PENDING"
        )
        db.add(slot)
        slots.append(slot)
        
    try:
        db.commit()
        for s in slots:
            db.refresh(s)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Không thể lưu danh sách cấp phát thùng: {str(e)}")
        
    return schemas.JobOrderDetailsResponse(
        job_order=job_order,
        total_qty=total_qty,
        total_cartons=total_cartons,
        product=schemas.JobOrderProductResponse.model_validate(product),
        slots=[schemas.JobOrderSlotResponse.model_validate(s) for s in slots]
    )

def get_job_order_slots_list(db: Session, job_order: str):
    slots = db.query(models.JobOrderCartonSlot).filter(
        models.JobOrderCartonSlot.job_order == job_order
    ).order_by(models.JobOrderCartonSlot.carton_number).all()
    
    return [schemas.JobOrderSlotResponse.model_validate(s) for s in slots]
