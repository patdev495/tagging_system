from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from src.core.models import Carton, Product, Customer
from src.features.carton.sn_allocator import plan_next_carton_sn

from . import schemas


def get_all_products(db: Session, customer_code: Optional[str] = None, search: Optional[str] = None):
    query = db.query(Product)
    if customer_code:
        query = query.join(Customer).filter(Customer.code == customer_code)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Product.item_name.ilike(search_filter),
                Product.factory_pn.ilike(search_filter),
                Product.asin.ilike(search_filter),
                Product.mfr_pn.ilike(search_filter),
                Product.product_desc.ilike(search_filter),
            )
        )
    return query.all()


def get_products_by_customer(customer_id: int, db: Session):
    return db.query(Product).filter(Product.customer_id == customer_id).all()


def get_product_by_id(product_id: int, db: Session):
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product_by_id(product_id, db)
    if not db_product:
        return None

    update_data = product.model_dump(exclude_unset=True)
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

    if product.template_type == "a11_tem2":
        from src.features.carton.sscc_allocator import plan_next_sscc_carton_sn
        plan = plan_next_sscc_carton_sn(db, product)
        return {
            "next_seq": plan.sequence,
            "next_sn": plan.carton_sn,
            "prefix": f"0{plan.company_prefix}",
            "sscc_text": plan.sscc_text,
            "check_digit": plan.check_digit,
        }

    if product.packing_mode == "weight_scale" or product.template_type == "a11":
        from src.features.carton.a11_sn_allocator import plan_next_a11_carton_sn
        plan = plan_next_a11_carton_sn(db, product, custom_yymm=yymm)
        return {"next_seq": plan.sequence, "next_sn": plan.carton_sn, "prefix": plan.prefix, "yymm": plan.yymm}

    plan = plan_next_carton_sn(db, product, custom_yymm=yymm, include_slots=True)
    return {"next_seq": plan.sequence, "next_sn": plan.carton_sn, "prefix": plan.prefix}



def get_last_carton(product_id: int, db: Session):
    carton = db.query(Carton).options(joinedload(Carton.items)).filter(
        Carton.product_id == product_id,
        Carton.status.in_(["SUCCESS", "PRINTED"]),
    ).order_by(Carton.id.desc()).first()

    if carton:
        items = getattr(carton, "items", None)
        carton.items_count = len(items) if isinstance(items, (list, tuple)) else 0

    return carton
