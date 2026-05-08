from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from src.core import models
from typing import Optional

def get_cartons(
    db: Session, 
    skip: int = 0, 
    limit: int = 50, 
    search: Optional[str] = None,
    product_id: Optional[int] = None,
    status: Optional[str] = None
):
    query = db.query(models.Carton).options(joinedload(models.Carton.product))
    
    if search:
        query = query.filter(models.Carton.carton_sn.like(f"%{search}%"))
    if product_id:
        query = query.filter(models.Carton.product_id == product_id)
    if status:
        query = query.filter(models.Carton.status == status)
        
    total = query.count()
    items = query.order_by(models.Carton.id.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "items": items}

def get_carton_detail(db: Session, carton_id: int):
    carton = db.query(models.Carton).options(
        joinedload(models.Carton.product),
        joinedload(models.Carton.items)
    ).filter(models.Carton.id == carton_id).first()
    
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
        
    carton.items_count = len(carton.items)
    return carton

def search_carton_by_sn(carton_sn: str, db: Session):
    carton = db.query(models.Carton).filter(models.Carton.carton_sn == carton_sn).order_by(models.Carton.id.desc()).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    
    return get_carton_detail(db, carton.id)

def search_by_item_sn(item_sn: str, db: Session):
    # Find the item first
    item = db.query(models.CartonItem).filter(models.CartonItem.item_sn == item_sn).order_by(models.CartonItem.id.desc()).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item S/N not found in any carton")
    
    # Return the associated carton with details
    return get_carton_detail(db, item.carton_id)

def delete_carton(db: Session, carton_id: int):
    carton = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    
    # Delete associated items first (if no cascade delete in models)
    db.query(models.CartonItem).filter(models.CartonItem.carton_id == carton_id).delete()
    
    # Delete the carton
    db.delete(carton)
    db.commit()
    return {"message": "Carton deleted successfully"}
