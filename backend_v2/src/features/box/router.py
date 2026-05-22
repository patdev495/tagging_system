from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.features.history.schemas import CartonDetail  # Import CartonDetail for Output
from . import schemas, service

router = APIRouter(prefix="/cartons", tags=["Box"])

@router.post("", response_model=CartonDetail)
def create_carton(carton_in: schemas.CartonCreate, request: Request, db: Session = Depends(get_db)):
    """Đóng gói và sinh XML"""
    # Ghi đè station_id bằng IP thật của Client
    client_ip = request.headers.get("X-Forwarded-For") or (request.client.host if request.client else "127.0.0.1")
    carton_in.station_id = client_ip
    
    new_carton, btxml_content = service.create_carton(carton_in, db)
    
    response_data = CartonDetail.model_validate(new_carton)
    response_data.btxml = btxml_content
    return response_data

@router.put("/rescan", response_model=CartonDetail)
def rescan_carton(rescan_in: schemas.CartonRescan, request: Request, db: Session = Depends(get_db)):
    """Xảo lại mã con hàng cho một thùng đã tồn tại và sinh lại XML đóng gói mới"""
    # Ghi đè station_id bằng IP thật của Client
    client_ip = request.headers.get("X-Forwarded-For") or (request.client.host if request.client else "127.0.0.1")
    rescan_in.station_id = client_ip
    
    updated_carton, btxml_content = service.rescan_carton(rescan_in, db)
    response_data = CartonDetail.model_validate(updated_carton)
    response_data.btxml = btxml_content
    return response_data
