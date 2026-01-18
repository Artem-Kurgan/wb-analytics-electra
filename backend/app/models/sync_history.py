from datetime import datetime
import enum
from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey, Enum, Index
from backend.app.db.base_class import Base

class SyncType(str, enum.Enum):
    stocks = "stocks"
    sales = "sales"
    orders = "orders"
    products = "products"

class SyncStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    in_progress = "in_progress"

class SyncHistory(Base):
    __tablename__ = "sync_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cabinet_id = Column(Integer, ForeignKey('cabinets.id', ondelete='CASCADE'), nullable=False)
    sync_type = Column(Enum(SyncType), nullable=False)
    last_sync_date = Column(DateTime, nullable=False)
    status = Column(Enum(SyncStatus), nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_sync_cabinet_type', 'cabinet_id', 'sync_type'),
    )
