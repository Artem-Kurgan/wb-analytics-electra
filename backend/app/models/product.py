from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.base_class import Base

class Product(Base):
    __tablename__ = "products"

    nm_id = Column(BigInteger, primary_key=True, comment="Артикул WB")
    cabinet_id = Column(Integer, ForeignKey('cabinets.id', ondelete='CASCADE'), nullable=False)
    vendor_code = Column(String(100), nullable=True, index=True, comment="Артикул продавца")
    barcode = Column(String(50), nullable=True)
    title = Column(String(500), nullable=True)
    manager = Column(String(255), nullable=True, index=True, comment="Теги менеджера из WB")
    image_url = Column(String(500), nullable=True)
    stock_wb = Column(Integer, default=0, comment="Остаток на WB")
    stock_own = Column(Integer, default=0, comment="Остаток своего склада")
    last_update = Column(DateTime, nullable=True)
    sizes = Column(JSON, nullable=True, comment="Массив размеров с баркодами")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_product_cabinet_manager', 'cabinet_id', 'manager'),
    )

    cabinet = relationship("Cabinet", back_populates="products")
    sales = relationship("SalesHistory", back_populates="product")
