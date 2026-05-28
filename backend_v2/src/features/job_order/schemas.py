from pydantic import BaseModel
from typing import List, Optional
import datetime

class JobOrderSlotResponse(BaseModel):
    id: int
    box_number: int
    carton_sn: str
    status: str
    scanned_at: Optional[datetime.datetime] = None
    carton_id: Optional[int] = None

    class Config:
        from_attributes = True

class JobOrderProductResponse(BaseModel):
    id: int
    item_name: str
    upc: str
    packed_qty: int
    start_part: Optional[str] = ""
    middle_part: Optional[str] = ""
    template_type: Optional[str] = "standard"
    template_path: Optional[str] = None
    allow_partial: Optional[int] = 0

    class Config:
        from_attributes = True

class JobOrderDetailsResponse(BaseModel):
    job_order: str
    total_qty: int
    total_boxes: int
    product: JobOrderProductResponse
    slots: List[JobOrderSlotResponse]

    class Config:
        from_attributes = True
