from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.core.database import get_db
from . import schemas, service
from typing import Optional

router = APIRouter(prefix="/cartons", tags=["History"])

@router.get("", response_model=schemas.CartonListResponse)
def list_cartons(
    skip: int = 0, 
    limit: int = 50, 
    search: Optional[str] = None,
    product_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Lấy danh sách lịch sử thùng hàng (có phân trang và lọc)"""
    return service.get_cartons(db, skip, limit, search, product_id, status)

@router.get("/search", response_model=schemas.CartonDetail)
def search_carton(carton_sn: str, db: Session = Depends(get_db)):
    """Tìm kiếm thùng theo Carton Serial Number"""
    return service.search_carton_by_sn(carton_sn, db)

@router.get("/search/item", response_model=schemas.CartonDetail)
def search_by_item(item_sn: str, db: Session = Depends(get_db)):
    """Tìm kiếm thùng theo Serial Number của sản phẩm bên trong"""
    return service.search_by_item_sn(item_sn, db)

@router.get("/statistics", response_model=schemas.PackagingStatisticsResponse)
def get_statistics(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """Lấy thống kê sản lượng đóng gói và chi tiết theo ngày/sản phẩm"""
    return service.get_packaging_statistics(db, start_date, end_date)

@router.get("/job-order/{job_order}/statistics", response_model=schemas.JobOrderStatisticsResponse)
def get_job_order_statistics(job_order: str, db: Session = Depends(get_db)):
    """Lấy thống kê chi tiết của một lệnh sản xuất (Job Order)"""
    return service.get_job_order_statistics(db, job_order)

@router.get("/{carton_id}", response_model=schemas.CartonDetail)
def get_carton_detail(carton_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết một thùng hàng bao gồm danh sách S/N sản phẩm"""
    return service.get_carton_detail(db, carton_id)

@router.delete("/{carton_id}")
def delete_carton(carton_id: int, db: Session = Depends(get_db)):
    """Xóa một thùng hàng và toàn bộ S/N bên trong nó"""
    return service.delete_carton(db, carton_id)
