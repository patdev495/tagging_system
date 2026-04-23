from pydantic import BaseModel
from typing import List, Optional
import datetime
from src.features.product.schemas import Product

class CartonItemBase(BaseModel):
    item_sn: str

class CartonItem(CartonItemBase):
    id: int
    carton_id: int

    class Config:
        from_attributes = True

class Carton(BaseModel):
    id: int
    product_id: int
    carton_sn: str
    created_at: datetime.datetime
    packed_by: Optional[str] = None
    job_order: Optional[str] = None
    status: str = "FAILED"
    btxml: Optional[str] = None 
    is_reprint: Optional[int] = 0
    carton_origin: Optional[str] = None
    items: List[CartonItem] = [] 
    product: Optional[Product] = None
    
    class Config:
        from_attributes = True
