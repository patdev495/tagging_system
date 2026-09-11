from pydantic import BaseModel
from typing import List, Optional

class CartonCreate(BaseModel):
    product_id: int
    items: List[str] # List of scanned Item S/Ns
    template_path: Optional[str] = None
    printer_name: Optional[str] = None
    print_folder: Optional[str] = None
    job_order: Optional[str] = None
    slot_id: Optional[int] = None
    custom_sn: Optional[int] = None
    carton_origin: str = "VN"
    station_id: Optional[str] = None
    custom_yymm: Optional[str] = None

class CartonRescan(BaseModel):
    carton_sn: str
    items: List[str]
    template_path: Optional[str] = None
    printer_name: Optional[str] = None
    station_id: Optional[str] = None

class CartonWeighPackCreate(BaseModel):
    product_id: int
    weight: float
    po_number: Optional[str] = None
    lot_number: Optional[str] = None
    printer_name: Optional[str] = None
    template_path: Optional[str] = None
    station_id: Optional[str] = None
    carton_origin: str = "VN"
    custom_yymm: Optional[str] = None
    custom_sn: Optional[int] = None

