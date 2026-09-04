from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from src.core.database import get_db
from src.core.models import Product, Customer
from src.features.history.schemas import CartonDetail
from src.features.auth.dependencies import require_admin
from . import schemas, service

router = APIRouter(tags=["Products"])

@router.get("/customers/{customer_id}/products", response_model=List[schemas.Product])
def get_products_by_customer(customer_id: int, db: Session = Depends(get_db)):
    """Lấy danh sách sản phẩm theo khách hàng"""
    return service.get_products_by_customer(customer_id, db)

@router.get("/products", response_model=List[schemas.Product])
def get_all_products(customer_code: Optional[str] = None, db: Session = Depends(get_db)):
    """Lấy tất cả sản phẩm (cho trang Admin hoặc lọc theo customer_code)"""
    query = db.query(Product)
    if customer_code:
        query = query.join(Customer).filter(Customer.code == customer_code)
    return query.all()

@router.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin chi tiết một sản phẩm"""
    db_product = service.get_product_by_id(product_id, db)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.post("/products", response_model=schemas.Product, dependencies=[Depends(require_admin)])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Tạo sản phẩm mới (Chỉ dành cho Admin)"""
    return service.create_product(db, product)

@router.put("/products/{product_id}", response_model=schemas.Product, dependencies=[Depends(require_admin)])
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """Cập nhật thông tin sản phẩm (Chỉ dành cho Admin)"""
    db_product = service.update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/products/{product_id}", dependencies=[Depends(require_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Xóa sản phẩm (Chỉ dành cho Admin)"""
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
