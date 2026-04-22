from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from . import schemas, service

# Note: Prefix is /customers to match the standard nested REST endpoint /customers/{customer_id}/products
router = APIRouter(prefix="/customers", tags=["Products"])

@router.get("/{customer_id}/products", response_model=List[schemas.Product])
def get_products_by_customer(customer_id: int, db: Session = Depends(get_db)):
    """Lấy danh sách sản phẩm theo khách hàng"""
    return service.get_products_by_customer(customer_id, db)
