from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    leader = "leader"
    manager = "manager"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    allowed_tags = Column(String(500), nullable=True, comment="Теги через запятую для менеджеров")
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    cabinets = relationship("Cabinet", back_populates="user")
