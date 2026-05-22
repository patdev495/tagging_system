from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from src.core.database import get_db
from src.features.history.schemas import CartonDetail
from . import schemas, service

router = APIRouter(tags=["Products"])

@router.get("/customers/{customer_id}/products", response_model=List[schemas.Product])
def get_products_by_customer(customer_id: int, db: Session = Depends(get_db)):
    """Lấy danh sách sản phẩm theo khách hàng"""
    return service.get_products_by_customer(customer_id, db)

from src.core.models import Product

@router.get("/products", response_model=List[schemas.Product])
def get_all_products(db: Session = Depends(get_db)):
    """Lấy tất cả sản phẩm (cho trang Admin)"""
    return db.query(Product).all()

@router.post("/products", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Tạo sản phẩm mới"""
    return service.create_product(db, product)

@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """Cập nhật thông tin sản phẩm"""
    db_product = service.update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Xóa sản phẩm"""
    success = service.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@router.get("/products/{product_id}/next-sn")
def get_next_sn(product_id: int, yymm: Optional[str] = None, db: Session = Depends(get_db)):
    """Lấy S/N tiếp theo cho sản phẩm"""
    return service.get_next_sn(product_id, db, yymm)

@router.get("/products/{product_id}/last-carton", response_model=Optional[CartonDetail])
def get_last_carton(product_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin thùng hàng cuối cùng của sản phẩm"""
    return service.get_last_carton(product_id, db)
