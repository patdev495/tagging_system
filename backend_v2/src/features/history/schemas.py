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
    template_type: Optional[str] = "standard"
    template_path: Optional[str] = None
    
    class Config:
        from_attributes = True

class CartonBase(BaseModel):
    carton_sn: str
    job_order: Optional[str] = None
    packed_by: Optional[str] = None
    status: str
    created_at: datetime
    carton_origin: Optional[str] = "VN"
    station_id: Optional[str] = None
    items_count: Optional[int] = 0
    is_reprint: Optional[int] = 0
    reprint_count: Optional[int] = 0

class Carton(CartonBase):
    id: int
    product_id: int
    btxml: Optional[str] = None
    product: Optional[ProductInfo] = None
    
    class Config:
        from_attributes = True

class CartonDetail(Carton):
    items: List[CartonItem] = []
    print_history: List[CartonBase] = []

class CartonListResponse(BaseModel):
    total: int
    items: List[Carton]

class DailyStat(BaseModel):
    date: str
    total: int
    success: int
    reprint: int

class ProductStat(BaseModel):
    item_name: str
    total: int
    reprint: int

class PackagingStatisticsResponse(BaseModel):
    total_cartons: int
    success_cartons: int
    failed_cartons: int
    reprint_cartons: int
    total_items: int
    daily_breakdown: List[DailyStat]
    product_breakdown: List[ProductStat]


class JobOrderProductStat(BaseModel):
    product_id: int
    item_name: str
    total_cartons: int
    success_cartons: int
    failed_cartons: int


class JobOrderStatisticsResponse(BaseModel):
    job_order: str
    total_cartons: int
    success_cartons: int
    failed_cartons: int
    total_attempts: int
    reprint_attempts: int
    total_items: int
    product_breakdown: List[JobOrderProductStat]
    cartons: List[Carton]


