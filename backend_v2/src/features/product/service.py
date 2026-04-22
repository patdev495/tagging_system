from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.core import models

def get_products_by_customer(customer_id: int, db: Session):
    products = db.query(models.Product).filter(models.Product.customer_id == customer_id).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this customer")
    return products
