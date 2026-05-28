import os
import sys
import logging
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.core import models, utils
from src.features.print import schemas

from src.features.print.domain import BTXMLDocument

logger = logging.getLogger("PrintService")

MAX_SN_GRID = 40  # Maximum SN slots on the detailed label

def generate_btxml(carton: models.Carton, product: models.Product, items: List[str], template_path: str, printer_name: Optional[str] = None) -> str:
    # Use the unified domain object to build the document applying all validation and schema rules
    doc = BTXMLDocument.from_carton_data(
        carton=carton,
        product=product,
        items=items,
        template_path=template_path,
        printer_name=printer_name
    )
    
    template_type = getattr(product, 'template_type', 'standard') or 'standard'
    btxml_content = doc.to_xml(template_type=template_type)
    return btxml_content


def update_status(carton_id: int, status_update: schemas.CartonStatusUpdate, db: Session):
    carton = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    carton.status = status_update.status  # type: ignore
    
    if status_update.status == "SUCCESS" and carton.job_order:
        slot = db.query(models.JobOrderCartonSlot).filter(
            models.JobOrderCartonSlot.job_order == carton.job_order,
            models.JobOrderCartonSlot.carton_sn == carton.carton_sn
        ).first()
        if slot:
            slot.status = "SCANNED"
            slot.carton_id = carton.id
            import datetime
            slot.scanned_at = datetime.datetime.now()
            
    db.commit()
    db.refresh(carton)
    return carton


def download_carton_btxml(carton_id: int, template_path: Optional[str] = None, db: Optional[Session] = None):
    carton = db.query(models.Carton).filter(models.Carton.id == carton_id).first() if db else None
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    
    btxml_content = carton.btxml
    if not btxml_content and db:
        product = db.query(models.Product).filter(models.Product.id == carton.product_id).first()
        if carton.is_reprint == 1:
            original = db.query(models.Carton).filter(
                models.Carton.carton_sn == carton.carton_sn,
                models.Carton.is_reprint == 0
            ).first()
            item_sns = [item.item_sn for item in original.items] if original else []
        else:
            item_sns = [item.item_sn for item in carton.items]
            
        # Priority logic inside resolve_template_path: DB -> Client -> Default
        db_path = getattr(product, 'template_path', None)
        path_to_use = utils.resolve_template_path(primary_path=db_path, fallback_path=template_path)
        btxml_content = generate_btxml(carton, product, item_sns, path_to_use)
        
    return carton.carton_sn, btxml_content

def reprint_carton(carton_id: int, printer_name: Optional[str] = None, template_path: Optional[str] = None, station_id: Optional[str] = None, db: Optional[Session] = None):
    logger.info(f"Reprinting carton {carton_id} (printer={printer_name}, template={template_path})")
    if not db:
        raise HTTPException(status_code=500, detail="Database session not provided")
    original = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not original:
        logger.warning(f"Reprint failed: Carton {carton_id} not found in database")
        raise HTTPException(status_code=404, detail="Original carton not found")
    
    initial_status = "SUCCESS" if original.status == "SUCCESS" else "PRINTED"
    new_carton = models.Carton(
        product_id=original.product_id,
        carton_sn=original.carton_sn,
        job_order=original.job_order,
        packed_by=printer_name or original.packed_by,
        status=initial_status,
        is_reprint=1,
        carton_origin=original.carton_origin,
        station_id=station_id or original.station_id
    )
    db.add(new_carton)
    db.flush()
    
    product = db.query(models.Product).filter(models.Product.id == original.product_id).first()
    item_sns = [item.item_sn for item in original.items]
    # Priority logic inside resolve_template_path: DB -> Client -> Default
    db_path = getattr(product, 'template_path', None)
    path_to_use = utils.resolve_template_path(primary_path=db_path, fallback_path=template_path)
    btxml_content = generate_btxml(new_carton, product, item_sns, path_to_use, printer_name)
    new_carton.btxml = None  # type: ignore
    
    db.commit()
    db.refresh(new_carton)
    
    # In-memory assignment so FastAPI/Pydantic serialization returns it to the client (e.g. for MCP server)
    new_carton.btxml = btxml_content  # type: ignore
    
    return new_carton
