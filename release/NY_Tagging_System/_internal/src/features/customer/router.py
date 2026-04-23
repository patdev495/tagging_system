from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from . import schemas, service

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("", response_model=List[schemas.Customer])
def get_customers(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả khách hàng"""
    return service.get_all_customers(db)
