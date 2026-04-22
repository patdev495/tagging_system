from pydantic import BaseModel
from typing import List, Optional

class CartonCreate(BaseModel):
    product_id: int
    items: List[str] # List of scanned Item S/Ns
    template_path: Optional[str] = None
    printer_name: Optional[str] = None
    print_folder: Optional[str] = None
    job_order: Optional[str] = None
    custom_sn: Optional[int] = None
    carton_origin: str = "VN"
