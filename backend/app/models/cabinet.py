from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Cabinet(Base):
    __tablename__ = "cabinets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment="Название ИП")
    api_token = Column(Text, nullable=False, comment="Зашифрованный токен WB")
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="cabinet")
