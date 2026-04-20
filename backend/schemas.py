from pydantic import BaseModel
from typing import List, Optional
import datetime

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

class CustomerBase(BaseModel):
    code: str
    name: str

class Customer(CustomerBase):
    id: int
    
    class Config:
        from_attributes = True

# Carton & Packing Schemas
class CartonItemBase(BaseModel):
    item_sn: str

class CartonItem(CartonItemBase):
    id: int
    carton_id: int

    class Config:
        from_attributes = True

class CartonBase(BaseModel):
    product_id: int
    carton_sn: str
    packed_by: Optional[str] = None

class CartonCreate(BaseModel):
    product_id: int
    items: List[str] # List of scanned Item S/Ns
    template_path: Optional[str] = None
    printer_name: Optional[str] = None
    print_folder: Optional[str] = None
    job_order: Optional[str] = None

class Carton(BaseModel):
    id: int
    product_id: int
    carton_sn: str
    created_at: datetime.datetime
    packed_by: Optional[str] = None
    job_order: Optional[str] = None
    status: str = "FAILED"
    btxml: Optional[str] = None # Stores BTXML data
    items: List[CartonItem] = [] # Include nested items
    
    class Config:
        from_attributes = True

class CartonStatusUpdate(BaseModel):
    status: str # SUCCESS or FAILED
