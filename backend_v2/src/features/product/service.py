from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from pydantic import ValidationError

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

    if db_product.template_type == "erro_04":
        try:
            schemas.ProductCreate.model_validate({
                "customer_id": db_product.customer_id,
                "item_name": db_product.item_name,
                "upc": db_product.upc,
                "packed_qty": db_product.packed_qty,
                "template_type": db_product.template_type,
                "template_path": db_product.template_path,
                "packing_mode": db_product.packing_mode,
                "target_weight": db_product.target_weight,
                "min_weight": db_product.min_weight,
                "max_weight": db_product.max_weight,
                "weight_unit": db_product.weight_unit,
                "mfr_pn": db_product.mfr_pn,
                "revision": db_product.revision,
                "product_desc": db_product.product_desc,
                "factory_item_code": db_product.factory_item_code,
                "carton_id_prefix": db_product.carton_id_prefix,
            })
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

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

    if product.template_type == "erro_02":
        from src.features.carton.sscc_allocator import plan_next_sscc_carton_sn
        plan = plan_next_sscc_carton_sn(db, product)
        return {
            "next_seq": plan.sequence,
            "next_sn": plan.carton_sn,
            "prefix": f"0{plan.company_prefix}",
            "sscc_text": plan.sscc_text,
            "check_digit": plan.check_digit,
        }

    if product.template_type == "erro_03":
        from src.features.carton.erro_03_sn_allocator import plan_next_erro_03_carton_sn
        plan = plan_next_erro_03_carton_sn(db, product)
        return {
            "next_seq": plan.sequence,
            "next_sn": plan.carton_sn,
            "supplier_code": plan.supplier_code,
            "yymmdd": plan.yymmdd,
        }

    if product.template_type == "erro_04":
        from src.features.carton.erro_04_sn_allocator import plan_next_erro_04_carton_sn
        plan = plan_next_erro_04_carton_sn(db, product)
        return {
            "next_seq": plan.sequence,
            "next_sn": plan.carton_sn,
            "carton_id_prefix": plan.carton_id_prefix,
            "date_code": plan.date_code,
        }

    if product.packing_mode == "weight_scale" or product.template_type == "erro_01":
        from src.features.carton.erro_01_sn_allocator import plan_next_erro_01_carton_sn
        plan = plan_next_erro_01_carton_sn(db, product, custom_yymm=yymm)
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
