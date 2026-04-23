from pydantic import BaseModel

class ProductBase(BaseModel):
    item_name: str
    packed_qty: int
    start_part: str
    middle_part: str
    upc: str

class Product(ProductBase):
    id: int
    customer_id: int

    class Config:
        from_attributes = True
