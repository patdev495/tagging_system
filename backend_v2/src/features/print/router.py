from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from src.core.database import get_db
from src.features.history.schemas import Carton
from . import schemas, service
from .bartender_engine import bt_engine

router = APIRouter(prefix="/print", tags=["Print"])

# ===== Cấu hình & Máy in =====

@router.get("/config")
def get_print_config():
    """Trả về trạng thái BarTender Engine."""
    return {
        "bartender_ready": bt_engine.is_initialized,
    }

@router.get("/printers")
def get_available_printers():
    """Lấy danh sách máy in trực tiếp từ Windows."""
    printers = bt_engine.get_printers()
    return {"printers": printers}

# ===== In ấn =====

@router.patch("/carton/{carton_id}/status", response_model=Carton)
def update_carton_status(carton_id: int, status_update: schemas.CartonStatusUpdate, db: Session = Depends(get_db)):
    """Cập nhật trạng thái in của thùng (SUCCESS / FAILED)"""
    return service.update_status(carton_id, status_update, db)

@router.get("/carton/{carton_id}/btxml")
def download_carton_btxml(carton_id: int, template_path: Optional[str] = None, db: Session = Depends(get_db)):
    """Tải file .xml của thùng để in thủ công"""
    carton_sn, btxml_content = service.download_carton_btxml(carton_id, template_path, db)
    return Response(
        content=btxml_content,
        media_type="application/xml",
        headers={"Content-Disposition": f"attachment; filename=print_job_{carton_sn}.xml"}
    )

@router.post("/carton/{carton_id}/reprint", response_model=Carton)
def reprint_carton(carton_id: int, template_path: Optional[str] = None, printer_name: Optional[str] = None, db: Session = Depends(get_db)):
    """In lại thùng đã đóng gói (Tạo bản ghi mới với is_reprint=1)"""
    return service.reprint_carton(carton_id, printer_name, template_path, db)

@router.post("/carton/{carton_id}/server-print")
def server_print_carton(carton_id: int, printer_name: Optional[str] = None, fallback_template_path: Optional[str] = None, db: Session = Depends(get_db)):
    """In tem trực tiếp qua BarTender Engine (không cần Agent riêng)."""

    carton = db.query(service.models.Carton).filter(service.models.Carton.id == carton_id).first()
    if not carton:
        return {"success": False, "message": "Carton not found"}

    if not carton.btxml:
        return {"success": False, "message": "No BTXML data available for this carton"}

    # Gọi BarTender trực tiếp — không qua HTTP nữa
    result = bt_engine.print_xml(
        xml_content=carton.btxml,
        printer_name_override=printer_name,
        fallback_path=fallback_template_path,
    )

    # Cập nhật trạng thái
    if result["success"]:
        carton.status = "SUCCESS"
    else:
        carton.status = "FAILED"
    db.commit()

    return result
