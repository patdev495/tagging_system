from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from . import schemas, service

# Note: Prefix is /customers to match the standard nested REST endpoint /customers/{customer_id}/products
router = APIRouter(tags=["Products"])

@router.get("/customers/{customer_id}/products", response_model=List[schemas.Product])
def get_products_by_customer(customer_id: int, db: Session = Depends(get_db)):
    """Lấy danh sách sản phẩm theo khách hàng"""
    return service.get_products_by_customer(customer_id, db)

@router.get("/products/{product_id}/next-sn")
def get_next_sn(product_id: int, db: Session = Depends(get_db)):
    """Lấy S/N tiếp theo cho sản phẩm"""
    return service.get_next_sn(product_id, db)

@router.get("/products/{product_id}/last-carton")
def get_last_carton(product_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin thùng hàng cuối cùng của sản phẩm"""
    return service.get_last_carton(product_id, db)
