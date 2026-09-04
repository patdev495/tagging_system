from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.models import User
from src.features.auth.dependencies import get_current_user
from .schemas import DashboardStatsResponse
from .service import get_dashboard_stats

router = APIRouter(prefix="/admin/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_statistics(
    time_range: str = Query("today", pattern="^(today|7d|30d)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy toàn bộ số liệu thống kê vận hành thời gian thực cho Dashboard:
    - KPIs (tổng thùng, thành công, lỗi, reprint, sản phẩm con, tỷ lệ %)
    - Sản lượng theo giờ (Hourly throughput)
    - Phân bổ theo sản phẩm (Top products)
    - Danh sách 15 thùng mới nhất (Live feed)
    - Tình trạng hệ thống BarTender & máy in
    Hỗ trợ cả quyền Admin và QA.
    """
    return get_dashboard_stats(db=db, time_range=time_range)
