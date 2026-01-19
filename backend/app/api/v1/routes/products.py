from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, desc, and_
from app.core.dependencies import get_db, get_current_user
from app.models import Product, User, SalesHistory
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

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
    period: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список товаров.
    Если указан period (day, week, month, 3months), метрики считаются динамически по SalesHistory.
    """

    if period:
        # Calculate start date based on period
        now = datetime.utcnow().date()
        if period == 'day':
            start_date = now
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == '3months':
            start_date = now - timedelta(days=90)
        else:
            start_date = now - timedelta(days=7) # default

        # Aggregate SalesHistory
        query = (
            select(
                Product.nm_id,
                Product.vendor_code,
                Product.barcode,
                Product.title,
                Product.image_url,
                Product.manager,
                Product.stock_wb,
                Product.stock_own,
                Product.sizes,
                func.coalesce(func.sum(SalesHistory.orders_count), 0).label('orders'),
                func.coalesce(func.sum(SalesHistory.buyouts_count), 0).label('sales'),
                func.coalesce(func.sum(SalesHistory.revenue), 0).label('revenue')
            )
            .outerjoin(
                SalesHistory,
                and_(
                    Product.nm_id == SalesHistory.nm_id,
                    SalesHistory.date >= start_date
                )
            )
            .group_by(Product.nm_id)
        )
    else:
        # Return static Product fields (total/snapshot)
        query = select(
            Product.nm_id,
            Product.vendor_code,
            Product.barcode,
            Product.title,
            Product.image_url,
            Product.manager,
            Product.stock_wb,
            Product.stock_own,
            Product.sizes,
            Product.orders,
            Product.sales,
            Product.revenue
        )
    
    if cabinet_id:
        query = query.where(Product.cabinet_id == cabinet_id)
    
    if manager:
        query = query.where(Product.manager.contains(manager))

    result = await db.execute(query)
    
    # Map result to schema
    products_data = []
    for row in result.all():
        # When using group_by/aggregates, row is a tuple-like object with labeled columns
        products_data.append({
            "nm_id": row.nm_id,
            "vendor_code": row.vendor_code,
            "barcode": row.barcode,
            "title": row.title,
            "image_url": row.image_url,
            "manager": row.manager,
            "orders": row.orders,
            "sales": row.sales,
            "revenue": row.revenue,
            "stock_wb": row.stock_wb,
            "stock_own": row.stock_own,
            "sizes": row.sizes
        })

    return products_data

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
