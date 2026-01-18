from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.dependencies import get_db, get_current_user
from app.models import Product, User
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/products", tags=["products"])

class ProductSchema(BaseModel):
    nm_id: int
    vendor_code: Optional[str]
    barcode: Optional[str]
    title: str
    image_url: Optional[str]
    manager: Optional[str]
    orders: int
    sales: int
    revenue: float
    stock_wb: int
    stock_own: int
    sizes: Optional[List] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProductSchema])
async def list_products(
    cabinet_id: Optional[int] = None,
    manager: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список товаров"""
    query = select(Product)
    
    if cabinet_id:
        query = query.where(Product.cabinet_id == cabinet_id)
    
    if manager:
        query = query.where(Product.manager.contains(manager))
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return products

@router.get("/{nm_id}", response_model=ProductSchema)
async def get_product(
    nm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить товар по nm_id"""
    result = await db.execute(select(Product).where(Product.nm_id == nm_id))
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product
