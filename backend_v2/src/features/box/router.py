from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.features.history.schemas import Carton  # Tái sử dụng Carton schema từ History cho Output
from . import schemas, service

router = APIRouter(prefix="/cartons", tags=["Box"])

@router.post("", response_model=Carton)
def create_carton(carton_in: schemas.CartonCreate, db: Session = Depends(get_db)):
    """Đóng gói và sinh XML"""
    new_carton, btxml_content = service.create_carton(carton_in, db)
    
    # We use response_model which will validate it, but we need to inject the btxml
    # if we want the client to receive it directly. Pydantic from_attributes handles it,
    # but we can also manually attach it if it wasn't attached.
    # Fortunately `new_carton.btxml` is already populated.
    
    response_data = Carton.from_orm(new_carton)
    response_data.btxml = btxml_content
    return response_data

@router.put("/rescan", response_model=Carton)
def rescan_carton(rescan_in: schemas.CartonRescan, db: Session = Depends(get_db)):
    """Xảo lại mã con hàng cho một thùng đã tồn tại và sinh lại XML"""
    updated_carton, btxml_content = service.rescan_carton(rescan_in, db)
    response_data = Carton.from_orm(updated_carton)
    response_data.btxml = btxml_content
    return response_data
