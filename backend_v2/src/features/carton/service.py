from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core import models, utils
from src.features.carton import schemas, slot_lifecycle
from src.features.carton.erro_01_sn_allocator import plan_next_erro_01_carton_sn
from src.features.carton.sn_allocator import plan_next_carton_sn
from src.features.print.service import generate_btxml


def _plan_admin_erro_carton_sn(db: Session, product: models.Product, sequence: int):
    if sequence < 1:
        raise HTTPException(status_code=400, detail="Số thứ tự phải lớn hơn 0.")
    if product.template_type == "erro_02":
        from src.features.carton.sscc_allocator import plan_next_sscc_carton_sn
        return plan_next_sscc_carton_sn(db, product, custom_sequence=sequence, lock=True), None
    if product.template_type == "erro_03":
        from src.features.carton.erro_03_sn_allocator import plan_next_erro_03_carton_sn
        plan = plan_next_erro_03_carton_sn(db, product, custom_sequence=sequence, lock=True)
        return plan, plan.yymmdd
    if product.template_type == "erro_04":
        from src.features.carton.erro_04_sn_allocator import Erro04CartonSNPlan, format_erro_04_sequence, pd027032_date_code
        now = datetime.now()
        prefix = (product.carton_id_prefix or "").strip().upper()
        if prefix not in {"H", "K"}:
            raise HTTPException(status_code=400, detail="Erro 04 Product requires carton_id_prefix H or K.")
        return Erro04CartonSNPlan(
            carton_sn=f"{prefix}{pd027032_date_code(now)}{format_erro_04_sequence(sequence)}",
            sequence=sequence,
            date_code=now.strftime("%y%m%d"),
            carton_id_prefix=prefix,
        ), now.strftime("%y%m%d")
    if product.template_type == "erro_05":
        from src.features.carton.erro_05_sn_allocator import ERRO_05_DEFAULT_PREFIX, ERRO_05_MAX_SEQUENCE, ERRO_05_MIN_SEQUENCE, Erro05CartonSNPlan
        if not ERRO_05_MIN_SEQUENCE <= sequence <= ERRO_05_MAX_SEQUENCE:
            raise HTTPException(status_code=400, detail="Erro 05 sequence must be between 50001 and 99999.")
        now = datetime.now()
        prefix = (product.pkg_prefix or ERRO_05_DEFAULT_PREFIX).strip()
        date_code = f"{now.strftime('%y')}{now.isocalendar()[1]:02d}"
        return Erro05CartonSNPlan(
            carton_sn=f"{prefix}2{date_code}{sequence:05d}",
            sequence=sequence,
            date_code=date_code,
            pkg_prefix=prefix,
        ), date_code
    plan = plan_next_erro_01_carton_sn(db, product, custom_sequence=sequence, lock=True)
    return plan, plan.date_code


def create_admin_erro_carton(carton_in: schemas.AdminCartonCreate, admin_username: str, db: Session):
    product = db.query(models.Product).filter(models.Product.id == carton_in.product_id).with_for_update().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.customer or product.customer.code != "ERRO":
        raise HTTPException(status_code=400, detail="Tạo Carton Admin chỉ áp dụng cho khách hàng Erro.")
    if not carton_in.reason.strip():
        raise HTTPException(status_code=400, detail="Lý do tạo Carton Admin là bắt buộc.")
    if product.min_weight is not None and carton_in.weight < product.min_weight:
        raise HTTPException(status_code=400, detail=f"Weight {carton_in.weight}kg is below minimum tolerance {product.min_weight}kg.")
    if product.max_weight is not None and carton_in.weight > product.max_weight:
        raise HTTPException(status_code=400, detail=f"Weight {carton_in.weight}kg is above maximum tolerance {product.max_weight}kg.")
    if product.template_type == "erro_04" and not (carton_in.po_number and carton_in.po_number.strip()):
        raise HTTPException(status_code=400, detail="PO Number is required for Erro 04 cartons.")
    if product.template_type == "erro_04" and not (carton_in.lot_number and carton_in.lot_number.strip()):
        raise HTTPException(status_code=400, detail="Lot Number is required for Erro 04 cartons.")

    plan, date_code = _plan_admin_erro_carton_sn(db, product, carton_in.sequence)
    duplicate_filters = [models.Carton.carton_sn == plan.carton_sn, models.Carton.is_reprint == 0]
    if product.template_type == "erro_01":
        duplicate_filters.append(models.Carton.product_id == product.id)
    existing = db.query(models.Carton).filter(*duplicate_filters).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Sê-ri thùng {plan.carton_sn} đã tồn tại trong hệ thống.")
    try:
        carton = models.Carton(
            product_id=product.id, carton_sn=plan.carton_sn, packed_by=admin_username,
            status="FAILED", job_order=carton_in.job_order, carton_origin=carton_in.carton_origin,
            station_id="ADMIN", weight=carton_in.weight, po_number=carton_in.po_number,
            lot_number=carton_in.lot_number or (datetime.now().strftime("%Y%m%d") if product.template_type == "erro_05" else None),
            date_code=date_code, admin_creation_reason=carton_in.reason.strip(), is_reprint=0,
        )
        db.add(carton)
        db.flush()
        template_path = utils.resolve_template_path(getattr(product, "template_path", None), carton_in.template_path)
        btxml_content = generate_btxml(carton, product, [], template_path, carton_in.printer_name)
        carton.btxml = btxml_content
        db.commit()
        db.refresh(carton)
        return carton, btxml_content
    except HTTPException:
        db.rollback()
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {error!s}") from error


def get_next_carton_sn(db: Session, product: models.Product, custom_sn: int | None = None, custom_yymm: str | None = None) -> str:
    return plan_next_carton_sn(
        db,
        product,
        custom_sn=custom_sn,
        custom_yymm=custom_yymm,
        include_slots=True,
        lock=True,
    ).carton_sn

def create_carton(carton_in: schemas.CartonCreate, db: Session):
    # Lock the product row to serialize carton creation for this product
    product = db.query(models.Product).filter(models.Product.id == carton_in.product_id).with_for_update().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if len(carton_in.items) != len(set(carton_in.items)):
        raise HTTPException(status_code=400, detail="Duplicate item S/Ns found in scan")

    # Validation: Check capacity and partial packing
    packed_qty = product.packed_qty or 0
    if packed_qty and len(carton_in.items) > packed_qty:
        raise HTTPException(
            status_code=400,
            detail=f"Carton capacity exceeded. Maximum is {product.packed_qty} items, but got {len(carton_in.items)}."
        )
    allow_partial = getattr(product, 'allow_partial', 0) or 0
    if not allow_partial and packed_qty and len(carton_in.items) < packed_qty:
        raise HTTPException(
            status_code=400, 
            detail=f"Partial packing is not allowed for this product. Expected {product.packed_qty} items, but got {len(carton_in.items)}."
        )

    slot = slot_lifecycle.get_pending_slot_for_carton_creation(
        db,
        slot_id=carton_in.slot_id,
        job_order=carton_in.job_order,
        product_id=carton_in.product_id,
    )

    new_sn = slot.carton_sn
    
    if carton_in.custom_sn is not None or slot is not None:
        existing = db.query(models.Carton).filter(models.Carton.carton_sn == new_sn).first()
        if existing:
            status_val = str(getattr(existing, "status", ""))
            if status_val in ("PRINTED", "SUCCESS", "SHIPPED"):
                raise HTTPException(status_code=400, detail=f"Carton S/N '{new_sn}' is already in use (Status: {status_val}).")
            elif (
                status_val == "FAILED"
                and getattr(existing, "job_order", None) == carton_in.job_order
                and getattr(existing, "product_id", None) == carton_in.product_id
            ):
                # Reuse and update existing failed carton attempt
                existing.packed_by = carton_in.printer_name or "System"
                existing.carton_origin = carton_in.carton_origin
                existing.station_id = carton_in.station_id
                
                existing_id = getattr(existing, "id", None)
                db.query(models.CartonItem).filter(models.CartonItem.carton_id == existing_id).delete()
                for item_sn in carton_in.items:
                    db.add(models.CartonItem(carton_id=existing_id, item_sn=item_sn))
                
                db_path = getattr(product, 'template_path', None)
                path_to_use = utils.resolve_template_path(primary_path=db_path, fallback_path=carton_in.template_path)
                btxml_content = generate_btxml(
                    existing, 
                    product, 
                    carton_in.items, 
                    path_to_use, 
                    carton_in.printer_name
                )
                existing.btxml = btxml_content
                db.commit()
                db.refresh(existing)
                return existing, btxml_content
            else:
                raise HTTPException(status_code=400, detail=f"Carton S/N '{new_sn}' is already in use (Status: {status_val}).")

    try:
        new_carton = models.Carton(
            product_id=product.id,
            carton_sn=new_sn,
            packed_by=carton_in.printer_name or "System", 
            job_order=carton_in.job_order,
            status="FAILED",
            carton_origin=carton_in.carton_origin,
            station_id=carton_in.station_id
        )
        db.add(new_carton)
        db.flush()
        
        for item_sn in carton_in.items:
            db.add(models.CartonItem(carton_id=new_carton.id, item_sn=item_sn))
        
        # Priority logic inside resolve_template_path: DB -> Client -> Default
        db_path = getattr(product, 'template_path', None)
        path_to_use = utils.resolve_template_path(primary_path=db_path, fallback_path=carton_in.template_path)
        
        # Always generate XML if we have a path
        btxml_content = generate_btxml(
            new_carton, 
            product, 
            carton_in.items, 
            path_to_use, 
            carton_in.printer_name
        )
        new_carton.btxml = btxml_content  # type: ignore
            
        db.commit()
        db.refresh(new_carton)
        
        return new_carton, btxml_content
        
    except Exception as e:
        db.rollback()
        # You could use logger here
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e!s}")

def rescan_carton(rescan_in: schemas.CartonRescan, db: Session):
    carton = db.query(models.Carton).filter(models.Carton.carton_sn == rescan_in.carton_sn).order_by(models.Carton.id.desc()).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
        
    product = db.query(models.Product).filter(models.Product.id == carton.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product associated with this carton was not found")
    
    if len(rescan_in.items) != len(set(rescan_in.items)):
        raise HTTPException(status_code=400, detail="Duplicate item S/Ns found in scan")
        
    # Validation: Check capacity and partial packing
    packed_qty = product.packed_qty or 0
    if packed_qty and len(rescan_in.items) > packed_qty:
        raise HTTPException(
            status_code=400,
            detail=f"Carton capacity exceeded. Maximum is {product.packed_qty} items, but got {len(rescan_in.items)}."
        )
    allow_partial = getattr(product, 'allow_partial', 0) or 0
    if not allow_partial and packed_qty and len(rescan_in.items) < packed_qty:
        raise HTTPException(
            status_code=400, 
            detail=f"Partial packing is not allowed for this product. Expected {product.packed_qty} items, but got {len(rescan_in.items)}."
        )

    try:
        # Delete old items
        db.query(models.CartonItem).filter(models.CartonItem.carton_id == carton.id).delete()
        
        # Insert new items
        for item_sn in rescan_in.items:
            db.add(models.CartonItem(carton_id=carton.id, item_sn=item_sn))
            
        # Default to FAILED until proven SUCCESS by printer agent later
        carton.status = "FAILED"  # type: ignore
        carton.btxml = None  # type: ignore
        carton.station_id = getattr(rescan_in, 'station_id', carton.station_id)  # type: ignore

        slot_lifecycle.release_original_slot_for_carton(db, carton)
        
        # Priority logic inside resolve_template_path: DB -> Client -> Default
        db_path = getattr(product, 'template_path', None)
        path_to_use = utils.resolve_template_path(primary_path=db_path, fallback_path=rescan_in.template_path)
        
        btxml_content = generate_btxml(
            carton, 
            product, 
            rescan_in.items, 
            path_to_use, 
            rescan_in.printer_name
        )
        carton.btxml = btxml_content  # type: ignore
            
        db.commit()
        db.refresh(carton)
        return carton, btxml_content
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e!s}")

def weigh_pack_carton(weigh_in: schemas.CartonWeighPackCreate, db: Session):
    product = db.query(models.Product).filter(models.Product.id == weigh_in.product_id).with_for_update().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # ADR 0006: Customer Erro strictly forbids manual sequence manipulation.
    customer_code = product.customer.code if product.customer else None
    if customer_code == "ERRO" and (weigh_in.custom_sn is not None or weigh_in.custom_yymm is not None):
        raise HTTPException(
            status_code=400,
            detail=f"Khách hàng {customer_code} không cho phép chỉnh sửa số thứ tự thùng thủ công (Manual sequence override is prohibited for {customer_code})."
        )

    # Weight tolerance checks
    if product.min_weight is not None and weigh_in.weight < product.min_weight:
        raise HTTPException(
            status_code=400,
            detail=f"Weight {weigh_in.weight}kg is below minimum tolerance {product.min_weight}kg."
        )
    if product.max_weight is not None and weigh_in.weight > product.max_weight:
        raise HTTPException(
            status_code=400,
            detail=f"Weight {weigh_in.weight}kg is above maximum tolerance {product.max_weight}kg."
        )

    # Allocate carton SN according to template type
    if product.template_type == "erro_02":
        from src.features.carton.sscc_allocator import plan_next_sscc_carton_sn
        plan = plan_next_sscc_carton_sn(
            db,
            product,
            custom_sequence=weigh_in.custom_sn,
            lock=True,
        )
        date_code = None
    elif product.template_type == "erro_03":
        from src.features.carton.erro_03_sn_allocator import plan_next_erro_03_carton_sn
        plan = plan_next_erro_03_carton_sn(
            db,
            product,
            custom_yymmdd=weigh_in.custom_yymm,
            custom_sequence=weigh_in.custom_sn,
            lock=True,
        )
        date_code = plan.yymmdd
    elif product.template_type == "erro_04":
        if not (weigh_in.po_number and weigh_in.po_number.strip()):
            raise HTTPException(status_code=400, detail="PO Number is required for Erro 04 cartons.")
        if not (weigh_in.lot_number and weigh_in.lot_number.strip()):
            raise HTTPException(status_code=400, detail="Lot Number is required for Erro 04 cartons.")
        from src.features.carton.erro_04_sn_allocator import plan_next_erro_04_carton_sn
        plan = plan_next_erro_04_carton_sn(db, product, lock=True)
        date_code = plan.date_code
    elif product.template_type == "erro_05":
        from src.features.carton.erro_05_sn_allocator import plan_next_erro_05_carton_sn
        plan = plan_next_erro_05_carton_sn(db, product, lock=True)
        date_code = plan.date_code
        if not (weigh_in.lot_number and weigh_in.lot_number.strip()):
            weigh_in.lot_number = datetime.now().strftime("%Y%m%d")
    else:
        plan = plan_next_erro_01_carton_sn(
            db,
            product,
            custom_yymm=weigh_in.custom_yymm,
            custom_sequence=weigh_in.custom_sn,
            lock=True,
        )
        date_code = plan.date_code

    if weigh_in.custom_sn:
        existing = db.query(models.Carton).filter(
            models.Carton.carton_sn == plan.carton_sn,
            models.Carton.is_reprint == 0,
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Sê-ri thùng {plan.carton_sn} đã tồn tại trong hệ thống!"
            )

    try:
        new_carton = models.Carton(
            product_id=product.id,
            carton_sn=plan.carton_sn,
            packed_by=weigh_in.printer_name or "System",
            status="FAILED",
            job_order=weigh_in.job_order,
            carton_origin=weigh_in.carton_origin,
            station_id=weigh_in.station_id,
            weight=weigh_in.weight,
            po_number=weigh_in.po_number,
            lot_number=weigh_in.lot_number,
            date_code=date_code,
            is_reprint=0,
        )
        db.add(new_carton)
        db.flush()

        db_path = getattr(product, 'template_path', None)
        path_to_use = utils.resolve_template_path(primary_path=db_path, fallback_path=weigh_in.template_path)

        btxml_content = generate_btxml(
            new_carton,
            product,
            [],
            path_to_use,
            weigh_in.printer_name
        )
        new_carton.btxml = btxml_content

        db.commit()
        db.refresh(new_carton)
        return new_carton, btxml_content

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e!s}")
