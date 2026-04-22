from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.core import models

def get_products_by_customer(customer_id: int, db: Session):
    products = db.query(models.Product).filter(models.Product.customer_id == customer_id).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this customer")
    return products

def get_next_sn(product_id: int, db: Session):
    # Find last SUCCESS carton for this product to get sequence
    last_carton = db.query(models.Carton).filter(
        models.Carton.product_id == product_id,
        models.Carton.status == "SUCCESS"
    ).order_by(models.Carton.id.desc()).first()
    
    if not last_carton:
        return {"next_seq": 1}
    
    try:
        sn = last_carton.carton_sn
        # The sequence is always the last 5 digits according to the rules
        seq_str = sn[-5:]
        if seq_str.isdigit():
            seq = int(seq_str)
            return {"next_seq": seq + 1}
        return {"next_seq": 1}
    except Exception:
        return {"next_seq": 1}

def get_last_carton(product_id: int, db: Session):
    return db.query(models.Carton).filter(
        models.Carton.product_id == product_id
    ).order_by(models.Carton.id.desc()).first()
