from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.core import models

def search_carton_by_sn(carton_sn: str, db: Session):
    carton = db.query(models.Carton).filter(models.Carton.carton_sn == carton_sn).order_by(models.Carton.id.desc()).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    return carton
