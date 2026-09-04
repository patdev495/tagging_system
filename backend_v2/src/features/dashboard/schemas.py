from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class KPIStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_cartons: int = 0
    success_cartons: int = 0
    failed_cartons: int = 0
    reprint_cartons: int = 0
    total_items: int = 0
    success_rate: float = 0.0
    error_rate: float = 0.0
    reprint_rate: float = 0.0

class HourlyStat(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hour: str
    total: int = 0
    success: int = 0
    failed: int = 0

class ProductStat(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_name: str
    customer_code: str
    count: int = 0
    percentage: float = 0.0

class LiveCartonFeed(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    carton_sn: str
    item_name: str
    customer_code: str
    created_at: datetime
    status: str
    is_reprint: int
    weight: Optional[float] = None
    station_id: Optional[str] = None
    items_count: int = 0

class SystemHealth(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bartender_status: str = "offline"  # "ready" | "offline"
    active_printers_count: int = 0

class DashboardStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    time_range: str
    kpis: KPIStats
    hourly_throughput: List[HourlyStat] = []
    top_products: List[ProductStat] = []
    live_feed: List[LiveCartonFeed] = []
    system: SystemHealth = SystemHealth()
