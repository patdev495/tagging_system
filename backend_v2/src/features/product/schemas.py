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

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True
