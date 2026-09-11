from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    item_name: str
    upc: Optional[str] = None
    packed_qty: int
    start_part: Optional[str] = "VN"
    middle_part: Optional[str] = ""
    template_type: Optional[str] = "standard"
    template_path: Optional[str] = None
    allow_partial: Optional[int] = 0
    customer_id: int
    packing_mode: Optional[str] = "item_scan"
    target_weight: Optional[float] = None
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None
    weight_unit: Optional[str] = "kg"
    mfr_pn: Optional[str] = None
    pkg_prefix: Optional[str] = None
    revision: Optional[str] = "B"
    factory_pn: Optional[str] = None
    asin: Optional[str] = None
    product_desc: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    item_name: Optional[str] = None
    upc: Optional[str] = None
    packed_qty: Optional[int] = None
    start_part: Optional[str] = None
    middle_part: Optional[str] = None
    template_type: Optional[str] = None
    template_path: Optional[str] = None
    allow_partial: Optional[int] = None
    customer_id: Optional[int] = None
    packing_mode: Optional[str] = None
    target_weight: Optional[float] = None
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None
    weight_unit: Optional[str] = None
    mfr_pn: Optional[str] = None
    pkg_prefix: Optional[str] = None
    revision: Optional[str] = None
    factory_pn: Optional[str] = None
    asin: Optional[str] = None
    product_desc: Optional[str] = None

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True

