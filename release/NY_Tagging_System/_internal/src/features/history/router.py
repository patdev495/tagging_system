from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db
from . import schemas, service

router = APIRouter(prefix="/cartons", tags=["History"])

@router.get("/search", response_model=schemas.Carton)
def search_carton(carton_sn: str, db: Session = Depends(get_db)):
    """Tìm kiếm thùng đã in thành công theo Serial Number"""
    return service.search_carton_by_sn(carton_sn, db)
