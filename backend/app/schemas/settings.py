from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CabinetCreate(BaseModel):
    name: str
    api_token: str

class CabinetResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: str
    allowed_tags: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    allowed_tags: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    allowed_tags: Optional[str] = None
    created_at: datetime
