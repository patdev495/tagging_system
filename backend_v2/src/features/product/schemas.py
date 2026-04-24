from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    item_name: str
    packed_qty: int
    start_part: str
    middle_part: str
    upc: str

class Product(ProductBase):
    id: int
    customer_id: int
    template_type: Optional[str] = "standard"
    allow_partial: Optional[int] = 0

    class Config:
        from_attributes = True
