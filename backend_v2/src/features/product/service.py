from typing import Optional

from sqlalchemy.orm import Session, joinedload

from src.core.models import Carton, Product
from src.features.carton.sn_allocator import plan_next_carton_sn

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
        return {"next_seq": 1, "next_sn": None, "prefix": ""}

    plan = plan_next_carton_sn(db, product, custom_yymm=yymm, include_slots=True)
    return {"next_seq": plan.sequence, "next_sn": plan.carton_sn, "prefix": plan.prefix}


def get_last_carton(product_id: int, db: Session):
    carton = db.query(Carton).options(joinedload(Carton.items)).filter(
        Carton.product_id == product_id,
        Carton.status.in_(["SUCCESS", "PRINTED"]),
    ).order_by(Carton.id.desc()).first()

    if carton:
        carton.items_count = len(carton.items) if carton.items is not None else 0

    return carton
