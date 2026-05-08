from sqlalchemy.orm import Session
from src.core.models import Product, Carton
from . import schemas

def get_products_by_customer(customer_id: int, db: Session):
    return db.query(Product).filter(Product.customer_id == customer_id).all()

def get_product_by_id(product_id: int, db: Session):
    return db.query(Product).filter(Product.id == product_id).first()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product_by_id(product_id, db)
    if not db_product:
        return None
    
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product_by_id(product_id, db)
    if not db_product:
        return False
    
    db.delete(db_product)
    db.commit()
    return True

def get_next_sn(product_id: int, db: Session, yymm: Optional[str] = None):
    product = get_product_by_id(product_id, db)
    if not product:
        return {"next_seq": 1}
        
    import datetime
    if not yymm:
        yymm = datetime.datetime.now().strftime("%y%m")
        
    prefix = f"{product.start_part or ''}{yymm}{product.middle_part or ''}"
    
    # Lấy tất cả carton trong tháng này để tìm max seq
    cartons = db.query(Carton).filter(
        Carton.product_id == product_id,
        Carton.status == 'SUCCESS',
        Carton.carton_sn.like(f"{prefix}%")
    ).all()
    
    if not cartons:
        return {"next_seq": 1}
    
    max_seq = 0
    for c in cartons:
        try:
            # Tìm phần số ở cuối (thường là 5 chữ số nhưng có thể thay đổi)
            import re
            match = re.search(r'(\d+)$', c.carton_sn)
            if match:
                seq = int(match.group(1))
                if seq > max_seq:
                    max_seq = seq
        except:
            pass
    
    return {"next_seq": max_seq + 1}

def get_last_carton(product_id: int, db: Session):
    carton = db.query(Carton).filter(
        Carton.product_id == product_id,
        Carton.status == 'SUCCESS'
    ).order_by(Carton.carton_sn.desc()).first()
    
    if carton:
        # Count items in this carton
        from src.core.models import CartonItem
        carton.items_count = db.query(CartonItem).filter(CartonItem.carton_id == carton.id).count()
        
    return carton
