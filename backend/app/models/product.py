from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Product(Base):
    __tablename__ = "products"

    nm_id = Column(BigInteger, primary_key=True)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id"), nullable=False)
    vendor_code = Column(String(100))
    barcode = Column(String(50))
    title = Column(String(500))
    image_url = Column(String(500))
    manager = Column(String(200))
    
    sizes = Column(JSON, default=list)
    
    stock_wb = Column(Integer, default=0)
    stock_own = Column(Integer, default=0)
    
    orders = Column(Integer, default=0)
    sales = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    last_update = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cabinet = relationship("Cabinet", back_populates="products")
