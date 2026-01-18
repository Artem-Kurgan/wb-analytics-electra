from datetime import datetime
from sqlalchemy import Column, Integer, Date, DateTime, BigInteger, ForeignKey, Numeric, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.base_class import Base

class SalesHistory(Base):
    __tablename__ = "sales_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nm_id = Column(BigInteger, ForeignKey('products.nm_id', ondelete='CASCADE'), nullable=False)
    cabinet_id = Column(Integer, ForeignKey('cabinets.id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    orders_count = Column(Integer, default=0)
    buyouts_count = Column(Integer, default=0)
    revenue = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_sales_nm_date', 'nm_id', 'date'),
        Index('idx_sales_cabinet_date', 'cabinet_id', 'date'),
        UniqueConstraint('nm_id', 'date', name='uq_sales_nm_date'),
    )

    product = relationship("Product", back_populates="sales")
