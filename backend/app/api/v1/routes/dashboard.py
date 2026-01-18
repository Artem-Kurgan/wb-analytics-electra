from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List, Optional
from app.db.session import get_db
from app.models import Product, SalesHistory, Cabinet
from app.schemas.dashboard import KPIResponse, ProductListResponse, ProductItem, ChartDataResponse
from app.core.dependencies import get_current_user, require_role
from app.models.user import User

# Enforce role requirement for all endpoints in this router
router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(require_role(["admin", "manager"]))]
)

def get_user_tags(user: User) -> List[str]:
    """Helper to parse allowed tags from user"""
    return [tag.strip() for tag in (user.allowed_tags or "").split(",")]

@router.get("/kpi", response_model=KPIResponse)
async def get_kpi(
    period: str = Query("week", regex="^(day|week|month|3months)$"),
    cabinet_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить KPI метрики за период"""

    # Определить date_from на основе period
    period_map = {
        'day': 1,
        'week': 7,
        'month': 30,
        '3months': 90
    }
    days = period_map[period]
    date_from = datetime.utcnow().date() - timedelta(days=days)
    date_from_prev = date_from - timedelta(days=days)

    # Базовый запрос
    query = select(
        func.sum(SalesHistory.revenue).label('total_revenue'),
        func.sum(SalesHistory.orders_count).label('total_orders'),
        func.sum(SalesHistory.buyouts_count).label('total_buyouts')
    ).where(SalesHistory.date >= date_from)

    # Фильтр по кабинету
    if cabinet_id:
        query = query.where(SalesHistory.cabinet_id == cabinet_id)

    # Фильтр для менеджеров
    if current_user.role == 'manager':
        user_tags = get_user_tags(current_user)
        # Using explicit join condition for safety
        query = query.join(Product, SalesHistory.nm_id == Product.nm_id).where(Product.manager.in_(user_tags))

    result = await db.execute(query)
    current = result.one()

    # Запрос для предыдущего периода
    query_prev = select(
        func.sum(SalesHistory.revenue).label('total_revenue'),
        func.sum(SalesHistory.orders_count).label('total_orders'),
        func.sum(SalesHistory.buyouts_count).label('total_buyouts')
    ).where(
        SalesHistory.date >= date_from_prev,
        SalesHistory.date < date_from
    )

    if cabinet_id:
        query_prev = query_prev.where(SalesHistory.cabinet_id == cabinet_id)

    if current_user.role == 'manager':
        user_tags = get_user_tags(current_user)
        query_prev = query_prev.join(Product, SalesHistory.nm_id == Product.nm_id).where(Product.manager.in_(user_tags))

    result_prev = await db.execute(query_prev)
    previous = result_prev.one()

    # Вычисление процентов изменения
    def calc_change(curr, prev):
        if not prev or prev == 0:
            return 0.0
        return round(((curr - prev) / prev) * 100, 1)

    total_revenue = float(current.total_revenue or 0)
    total_orders = int(current.total_orders or 0)
    total_buyouts = int(current.total_buyouts or 0)

    revenue_change = calc_change(total_revenue, float(previous.total_revenue or 0))
    orders_change = calc_change(total_orders, int(previous.total_orders or 0))

    # Средний % выкупа
    avg_buyout_rate = round((total_buyouts / total_orders * 100), 1) if total_orders > 0 else 0.0

    # Средний чек
    avg_check = round(total_revenue / total_buyouts, 2) if total_buyouts > 0 else 0.0

    # Товары с низким остатком
    low_stock_query = select(func.count(Product.nm_id)).where(
        (Product.stock_wb + Product.stock_own) < 10
    )
    if cabinet_id:
        low_stock_query = low_stock_query.where(Product.cabinet_id == cabinet_id)
    if current_user.role == 'manager':
        user_tags = get_user_tags(current_user)
        low_stock_query = low_stock_query.where(Product.manager.in_(user_tags))

    result_low_stock = await db.execute(low_stock_query)
    low_stock_count = result_low_stock.scalar()

    return KPIResponse(
        total_revenue=total_revenue,
        revenue_change_percent=revenue_change,
        total_orders=total_orders,
        orders_change_percent=orders_change,
        total_buyouts=total_buyouts,
        avg_buyout_rate=avg_buyout_rate,
        avg_check=avg_check,
        low_stock_count=low_stock_count
    )

@router.get("/products", response_model=ProductListResponse)
async def get_products(
    period: str = Query("week"),
    cabinet_id: Optional[int] = None,
    sort_by: str = Query("revenue", regex="^(revenue|orders|buyouts|buyout_rate|stock)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=10, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список товаров с метриками"""

    # Период
    period_map = {'day': 1, 'week': 7, 'month': 30, '3months': 90}
    days = period_map.get(period, 7)
    date_from = datetime.utcnow().date() - timedelta(days=days)
    date_from_prev = date_from - timedelta(days=days)

    # Подзапрос для текущего периода
    subq_current = select(
        SalesHistory.nm_id,
        func.sum(SalesHistory.orders_count).label('orders'),
        func.sum(SalesHistory.buyouts_count).label('buyouts'),
        func.sum(SalesHistory.revenue).label('revenue')
    ).where(SalesHistory.date >= date_from).group_by(SalesHistory.nm_id).subquery()

    # Подзапрос для предыдущего периода
    subq_prev = select(
        SalesHistory.nm_id,
        func.sum(SalesHistory.orders_count).label('orders_prev'),
        func.sum(SalesHistory.buyouts_count).label('buyouts_prev'),
        func.sum(SalesHistory.revenue).label('revenue_prev')
    ).where(
        SalesHistory.date >= date_from_prev,
        SalesHistory.date < date_from
    ).group_by(SalesHistory.nm_id).subquery()

    # Основной запрос
    query = select(
        Product,
        subq_current.c.orders,
        subq_current.c.buyouts,
        subq_current.c.revenue,
        subq_prev.c.orders_prev,
        subq_prev.c.buyouts_prev,
        subq_prev.c.revenue_prev
    ).outerjoin(subq_current, Product.nm_id == subq_current.c.nm_id)\
     .outerjoin(subq_prev, Product.nm_id == subq_prev.c.nm_id)

    # Фильтры
    if cabinet_id:
        query = query.where(Product.cabinet_id == cabinet_id)

    if current_user.role == 'manager':
        user_tags = get_user_tags(current_user)
        query = query.where(Product.manager.in_(user_tags))

    # Сортировка
    if sort_by == 'revenue':
        col = subq_current.c.revenue
    elif sort_by == 'orders':
        col = subq_current.c.orders
    elif sort_by == 'buyouts':
        col = subq_current.c.buyouts
    elif sort_by == 'stock':
        col = Product.stock_wb + Product.stock_own
    else:
        col = subq_current.c.revenue # default

    if col is not None: # check just in case
        if order == 'desc':
            query = query.order_by(col.desc().nulls_last())
        else:
            query = query.order_by(col.asc().nulls_first())

    # Пагинация
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    # Формирование ответа
    items = []
    for row in rows:
        product = row[0]
        orders = int(row[1] or 0)
        buyouts = int(row[2] or 0)
        revenue = float(row[3] or 0)
        orders_prev = int(row[4] or 0)
        buyouts_prev = int(row[5] or 0)
        revenue_prev = float(row[6] or 0)

        # Вычисление динамики
        def calc_change(curr, prev):
            if not prev or prev == 0:
                return 0.0
            return round(((curr - prev) / prev) * 100, 1)

        buyout_rate = round((buyouts / orders * 100), 1) if orders > 0 else 0.0
        avg_check = round(revenue / buyouts, 2) if buyouts > 0 else 0.0

        items.append(ProductItem(
            nm_id=product.nm_id,
            vendor_code=product.vendor_code,
            barcode=product.barcode,
            title=product.title,
            manager=product.manager,
            image_url=product.image_url,
            orders=orders,
            orders_change_percent=calc_change(orders, orders_prev),
            buyouts=buyouts,
            buyouts_change_percent=calc_change(buyouts, buyouts_prev),
            buyout_rate=buyout_rate,
            revenue=revenue,
            revenue_change_percent=calc_change(revenue, revenue_prev),
            avg_check=avg_check,
            stock_wb=product.stock_wb,
            stock_own=product.stock_own,
            total_stock=product.stock_wb + product.stock_own
        ))

    # Подсчет total
    count_query = select(func.count(Product.nm_id))
    if cabinet_id:
        count_query = count_query.where(Product.cabinet_id == cabinet_id)
    if current_user.role == 'manager':
        user_tags = get_user_tags(current_user)
        count_query = count_query.where(Product.manager.in_(user_tags))

    result_count = await db.execute(count_query)
    total = result_count.scalar()

    return ProductListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/charts/sales-by-cabinet", response_model=ChartDataResponse)
async def get_sales_by_cabinet(
    period: str = Query("week", regex="^(day|week|month|3months)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """График продаж по кабинетам"""
    period_map = {'day': 1, 'week': 7, 'month': 30, '3months': 90}
    days = period_map[period]
    date_from = datetime.utcnow().date() - timedelta(days=days)

    query = select(
        Cabinet.title,
        func.sum(SalesHistory.revenue).label('total_revenue')
    ).join(SalesHistory, Cabinet.id == SalesHistory.cabinet_id)\
     .where(SalesHistory.date >= date_from)

    if current_user.role == 'manager':
        user_tags = get_user_tags(current_user)
        query = query.join(Product, SalesHistory.nm_id == Product.nm_id)\
                     .where(Product.manager.in_(user_tags))

    query = query.group_by(Cabinet.title)

    result = await db.execute(query)
    rows = result.all()

    data = []
    for row in rows:
        data.append({"name": row[0], "value": float(row[1] or 0)})

    return ChartDataResponse(title="Sales by Cabinet", type="pie", data=data)

@router.get("/charts/stock-distribution", response_model=ChartDataResponse)
async def get_stock_distribution(
    cabinet_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Распределение остатков (WB vs Свой склад)"""
    query = select(
        func.sum(Product.stock_wb).label('stock_wb'),
        func.sum(Product.stock_own).label('stock_own')
    )

    if cabinet_id:
        query = query.where(Product.cabinet_id == cabinet_id)

    if current_user.role == 'manager':
        user_tags = get_user_tags(current_user)
        query = query.where(Product.manager.in_(user_tags))

    result = await db.execute(query)
    row = result.one()

    data = [
        {"name": "Склад WB", "value": int(row[0] or 0)},
        {"name": "Свой склад", "value": int(row[1] or 0)}
    ]

    return ChartDataResponse(title="Stock Distribution", type="pie", data=data)

@router.post("/sync/{cabinet_id}")
async def sync_cabinet(
    cabinet_id: int,
    current_user: User = Depends(get_current_user),
    # db: AsyncSession = Depends(get_db)
):
    """Запустить синхронизацию кабинета"""
    # TODO: Добавить проверку прав на кабинет и запуск Celery задачи

    return {"status": "ok", "message": f"Sync started for cabinet {cabinet_id}"}
