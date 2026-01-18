from pydantic import BaseModel
from typing import List, Optional, Any

class KPIResponse(BaseModel):
    total_revenue: float
    revenue_change_percent: float
    total_orders: int
    orders_change_percent: float
    total_buyouts: int
    avg_buyout_rate: float
    avg_check: float
    low_stock_count: int

class ProductItem(BaseModel):
    nm_id: int
    vendor_code: Optional[str]
    barcode: Optional[str]
    title: Optional[str]
    manager: Optional[str]
    image_url: Optional[str]
    orders: int
    orders_change_percent: float
    buyouts: int
    buyouts_change_percent: float
    buyout_rate: float
    revenue: float
    revenue_change_percent: float
    avg_check: float
    stock_wb: int
    stock_own: int
    total_stock: int

class ProductListResponse(BaseModel):
    items: List[ProductItem]
    total: int
    page: int
    limit: int

class ChartDataPoint(BaseModel):
    name: str
    value: float
    extra: Optional[Any] = None

class ChartDataResponse(BaseModel):
    title: str
    type: str = "bar"
    data: List[ChartDataPoint]
