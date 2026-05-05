import os
import sys
import logging
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.core import models, utils
from src.features.print import schemas

logger = logging.getLogger("PrintService")

MAX_SN_GRID = 30  # Maximum SN slots on the detailed label

def _get_template_base_dir():
    """Get the correct base directory for XML templates, handling both dev and PyInstaller exe."""
    if getattr(sys, 'frozen', False):
        # PyInstaller --onedir: data files are in _internal/src/...
        # sys._MEIPASS points to _internal/
        meipass = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        frozen_path = os.path.join(meipass, "src", "features", "print")
        logger.info(f"[FROZEN] _MEIPASS={meipass}, template_dir={frozen_path}, exists={os.path.isdir(frozen_path)}")
        if os.path.isdir(frozen_path):
            return frozen_path
    
    # Dev mode: relative to this file
    return os.path.dirname(os.path.abspath(__file__))

def generate_btxml(carton: models.Carton, product: models.Product, items: List[str], template_path: str, printer_name: str = None) -> str:
    raw_origin = carton.carton_origin if carton.carton_origin else "VN"
    origin_text = "MADE IN CHINA" if raw_origin == "CN" else "MADE IN VIETNAM"
    qr_content = "&#xA;".join(items)
    printer_tag = f"<Printer>{printer_name}</Printer>" if printer_name else ""
    
    # Select template based on product.template_type
    template_type = getattr(product, 'template_type', 'standard') or 'standard'
    base_dir = _get_template_base_dir()
    template_file = os.path.join(base_dir, "templates", f"{template_type}.xml")
    
    logger.info(f"[BTXML] product.template_type='{product.template_type}' -> resolved='{template_type}', "
                f"base_dir='{base_dir}', template_file='{template_file}', "
                f"exists={os.path.exists(template_file)}, frozen={getattr(sys, 'frozen', False)}")
    
    # Diagnostic: list what's actually in the templates directory
    templates_dir = os.path.join(base_dir, "templates")
    if os.path.isdir(templates_dir):
        dir_contents = os.listdir(templates_dir)
        logger.info(f"[BTXML] templates/ dir contents: {dir_contents}")
    else:
        logger.warning(f"[BTXML] templates/ dir NOT FOUND at: {templates_dir}")
        # Try alternative: relative to __file__
        alt_base = os.path.dirname(os.path.abspath(__file__))
        alt_templates_dir = os.path.join(alt_base, "templates")
        logger.info(f"[BTXML] Trying __file__ fallback: __file__={__file__}, alt_base={alt_base}, alt_templates_dir={alt_templates_dir}, exists={os.path.isdir(alt_templates_dir)}")
        if os.path.isdir(alt_templates_dir):
            base_dir = alt_base
            template_file = os.path.join(base_dir, "templates", f"{template_type}.xml")
            logger.info(f"[BTXML] Using __file__ fallback! template_file={template_file}, exists={os.path.exists(template_file)}")
    
    # Fallback to base.xml if template doesn't exist
    if not os.path.exists(template_file):
        fallback_file = os.path.join(base_dir, "templates", "base.xml")
        logger.warning(f"[BTXML] Template '{template_file}' NOT FOUND! Falling back to '{fallback_file}' (exists={os.path.exists(fallback_file)})")
        template_file = fallback_file
        template_type = "standard"
    
    with open(template_file, "r", encoding="utf-8") as f:
        xml_template = f.read()
    
    # For partial packing, QTY = actual scanned count, not packed_qty
    allow_partial = getattr(product, 'allow_partial', 0) or 0
    actual_qty = len(items)
    if allow_partial:
        qty_text = f"{actual_qty}PCS"
    else:
        qty_text = f"{product.packed_qty}PCS"
        
    data_dict = {
        "template_path": template_path,
        "printer_tag": printer_tag,
        "item_name": product.item_name,
        "qty": qty_text,
        "carton_sn": carton.carton_sn,
        "upc": product.upc,
        "qr_content": qr_content,
        "origin_text": origin_text,
        "mac_id": f"MAC ID ({actual_qty})"
    }
    
    # Detailed template: generate SN grid tags dynamically
    if template_type == "detailed":
        sn_tags = []
        for i in range(MAX_SN_GRID):
            sn_value = items[i] if i < len(items) else " "
            sn_tags.append(f'            <NamedSubString Name="SN_{i+1}"><Value>{sn_value}</Value></NamedSubString>')
        data_dict["sn_grid_tags"] = "\n".join(sn_tags)
    
    # Simple string formatting for the template
    btxml_content = xml_template.format(**data_dict)
    return btxml_content.strip()

def update_status(carton_id: int, status_update: schemas.CartonStatusUpdate, db: Session):
    carton = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    carton.status = status_update.status
    db.commit()
    db.refresh(carton)
    return carton

def download_carton_btxml(carton_id: int, template_path: str = None, db: Session = None):
    carton = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    
    btxml_content = carton.btxml
    if not btxml_content:
        product = db.query(models.Product).filter(models.Product.id == carton.product_id).first()
        item_sns = [item.item_sn for item in carton.items]
        # Priority logic inside resolve_template_path: DB -> Client -> Default
        db_path = getattr(product, 'template_path', None)
        path_to_use = utils.resolve_template_path(primary_path=db_path, fallback_path=template_path)
        btxml_content = generate_btxml(carton, product, item_sns, path_to_use)
        
    return carton.carton_sn, btxml_content

def reprint_carton(carton_id: int, printer_name: str = None, template_path: str = None, station_id: str = None, db: Session = None):
    original = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Original carton not found")
    
    new_carton = models.Carton(
        product_id=original.product_id,
        carton_sn=original.carton_sn,
        job_order=original.job_order,
        packed_by=printer_name or original.packed_by,
        status="SUCCESS",
        is_reprint=1,
        carton_origin=original.carton_origin,
        station_id=station_id or original.station_id
    )
    db.add(new_carton)
    db.flush()
    
    for item in original.items:
        db.add(models.CartonItem(carton_id=new_carton.id, item_sn=item.item_sn))
    
    product = db.query(models.Product).filter(models.Product.id == original.product_id).first()
    item_sns = [item.item_sn for item in original.items]
    # Priority logic inside resolve_template_path: DB -> Client -> Default
    db_path = getattr(product, 'template_path', None)
    path_to_use = utils.resolve_template_path(primary_path=db_path, fallback_path=template_path)
    btxml_content = generate_btxml(new_carton, product, item_sns, path_to_use, printer_name)
    new_carton.btxml = btxml_content
    
    db.commit()
    db.refresh(new_carton)
    
    return new_carton
