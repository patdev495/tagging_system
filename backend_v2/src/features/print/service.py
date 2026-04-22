import os
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.core import models
from src.features.print import schemas

def generate_btxml(carton: models.Carton, product: models.Product, items: List[str], template_path: str, printer_name: str = None) -> str:
    raw_origin = carton.carton_origin if carton.carton_origin else "VN"
    origin_text = "MADE IN CHINA" if raw_origin == "CN" else "MADE IN VIETNAM"
    qr_content = "&#xA;".join(items)
    printer_tag = f"<Printer>{printer_name}</Printer>" if printer_name else ""
    
    # Path to the base template file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_file = os.path.join(base_dir, "templates", "base.xml")
    
    with open(template_file, "r", encoding="utf-8") as f:
        xml_template = f.read()
        
    data_dict = {
        "template_path": template_path,
        "printer_tag": printer_tag,
        "item_name": product.item_name,
        "qty": f"{product.packed_qty}PCS",
        "carton_sn": carton.carton_sn,
        "upc": product.upc,
        "qr_content": qr_content,
        "origin_text": origin_text
    }
    
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
        path_to_use = template_path or "D:\\Labels\\carton_ui.btw"
        btxml_content = generate_btxml(carton, product, item_sns, path_to_use)
        
    return carton.carton_sn, btxml_content

def reprint_carton(carton_id: int, printer_name: str = None, template_path: str = None, db: Session = None):
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
        carton_origin=original.carton_origin
    )
    db.add(new_carton)
    db.flush()
    
    for item in original.items:
        db.add(models.CartonItem(carton_id=new_carton.id, item_sn=item.item_sn))
    
    product = db.query(models.Product).filter(models.Product.id == original.product_id).first()
    item_sns = [item.item_sn for item in original.items]
    path_to_use = template_path or "D:\\Labels\\carton_ui.btw"
    btxml_content = generate_btxml(new_carton, product, item_sns, path_to_use, printer_name)
    new_carton.btxml = btxml_content
    
    db.commit()
    db.refresh(new_carton)
    
    return new_carton
