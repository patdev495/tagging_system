from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from src.core.database import get_db
from src.features.history.schemas import Carton  # Tái sử dụng Carton schema
from . import schemas, service

router = APIRouter(prefix="/cartons", tags=["Print"])

@router.patch("/{carton_id}/status", response_model=Carton)
def update_carton_status(carton_id: int, status_update: schemas.CartonStatusUpdate, db: Session = Depends(get_db)):
    """Cập nhật trạng thái in của thùng (SUCCESS / FAILED)"""
    return service.update_status(carton_id, status_update, db)

@router.get("/{carton_id}/btxml")
def download_carton_btxml(carton_id: int, template_path: Optional[str] = None, db: Session = Depends(get_db)):
    """Tải file .xml của thùng để in thủ công"""
    carton_sn, btxml_content = service.download_carton_btxml(carton_id, template_path, db)
    return Response(
        content=btxml_content, 
        media_type="application/xml", 
        headers={"Content-Disposition": f"attachment; filename=print_job_{carton_sn}.xml"}
    )

@router.post("/{carton_id}/reprint", response_model=Carton)
def reprint_carton(carton_id: int, template_path: Optional[str] = None, printer_name: Optional[str] = None, db: Session = Depends(get_db)):
    """In lại thùng đã đóng gói (Tạo bản ghi mới với is_reprint=1)"""
    return service.reprint_carton(carton_id, printer_name, template_path, db)
