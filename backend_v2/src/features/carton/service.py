import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from src.core import models, utils
from src.features.carton import schemas
from src.features.print.service import generate_btxml

def get_next_carton_sn(db: Session, product: models.Product, custom_sn: Optional[int] = None, custom_yymm: Optional[str] = None) -> str:
    if custom_yymm:
        yymm = custom_yymm
    else:
        now = datetime.datetime.now()
        yymm = now.strftime("%y%m")
    
    prefix = f"{product.start_part}{yymm}{product.middle_part}"
    
    if custom_sn is not None:
        return f"{prefix}{str(custom_sn).zfill(5)}"
        
    # Lock for update to prevent duplicate carton generation concurrently
    max_sn = db.query(func.max(models.Carton.carton_sn)).filter(
        models.Carton.carton_sn.like(f"{prefix}%"),
        models.Carton.is_reprint == 0
    ).with_for_update().scalar()
    
    if max_sn:
        try:
            next_seq = int(max_sn[-5:]) + 1
        except:
            next_seq = 1
    else:
        next_seq = 1
    return f"{prefix}{str(next_seq).zfill(5)}"

def create_carton(carton_in: schemas.CartonCreate, db: Session):
    # Lock the product row to serialize carton creation for this product
    product = db.query(models.Product).filter(models.Product.id == carton_in.product_id).with_for_update().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if len(carton_in.items) != len(set(carton_in.items)):
        raise HTTPException(status_code=400, detail="Duplicate item S/Ns found in scan")
    
    # Validation: Check capacity and partial packing
    if len(carton_in.items) > product.packed_qty:
        raise HTTPException(
            status_code=400,
            detail=f"Carton capacity exceeded. Maximum is {product.packed_qty} items, but got {len(carton_in.items)}."
        )
    allow_partial = getattr(product, 'allow_partial', 0) or 0
    if not allow_partial and len(carton_in.items) < product.packed_qty:
        raise HTTPException(
            status_code=400, 
            detail=f"Partial packing is not allowed for this product. Expected {product.packed_qty} items, but got {len(carton_in.items)}."
        )
    
    new_sn = get_next_carton_sn(db, product, carton_in.custom_sn, carton_in.custom_yymm)
    
    if carton_in.custom_sn is not None:
        existing = db.query(models.Carton).filter(models.Carton.carton_sn == new_sn).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"S/N (Seq: {carton_in.custom_sn}) is already in use (Status: {existing.status}).")

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
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

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
    if len(rescan_in.items) > product.packed_qty:
        raise HTTPException(
            status_code=400,
            detail=f"Carton capacity exceeded. Maximum is {product.packed_qty} items, but got {len(rescan_in.items)}."
        )
    allow_partial = getattr(product, 'allow_partial', 0) or 0
    if not allow_partial and len(rescan_in.items) < product.packed_qty:
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
        carton.station_id = getattr(rescan_in, 'station_id', carton.station_id)
        
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
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
