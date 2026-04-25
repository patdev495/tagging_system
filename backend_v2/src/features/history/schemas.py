from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CartonItem(BaseModel):
    id: int
    item_sn: str
    
    class Config:
        from_attributes = True

class ProductInfo(BaseModel):
    id: int
    item_name: str
    upc: Optional[str] = None
    packed_qty: Optional[int] = 1
    allow_partial: Optional[int] = 0
    start_part: Optional[str] = ""
    middle_part: Optional[str] = ""
    
    class Config:
        from_attributes = True

class CartonBase(BaseModel):
    carton_sn: str
    job_order: Optional[str] = None
    packed_by: Optional[str] = None
    status: str
    created_at: datetime
    carton_origin: Optional[str] = "VN"
    items_count: Optional[int] = 0
    is_reprint: Optional[int] = 0

class Carton(CartonBase):
    id: int
    product_id: int
    btxml: Optional[str] = None
    product: Optional[ProductInfo] = None
    
    class Config:
        from_attributes = True

class CartonDetail(Carton):
    items: List[CartonItem] = []

class CartonListResponse(BaseModel):
    total: int
    items: List[Carton]
