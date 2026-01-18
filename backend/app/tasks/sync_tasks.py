from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy import select, update
from app.db.session import async_session
from app.models import Cabinet, Product, SalesHistory, SyncHistory
from app.services.wb_api import WildberriesAPIClient
import structlog

log = structlog.get_logger()

@shared_task(bind=True, max_retries=3)
async def sync_products(self, cabinet_id: int):
    """Синхронизация карточек товаров с тегами"""
    async with async_session() as session:
        try:
            # Обновить статус на in_progress
            await session.execute(
                update(SyncHistory)
                .where(SyncHistory.cabinet_id == cabinet_id, SyncHistory.sync_type == 'products')
                .values(status='in_progress', last_sync_date=datetime.utcnow())
            )
            await session.commit()

            # Получить кабинет
            cabinet = await session.get(Cabinet, cabinet_id)
            if not cabinet:
                raise ValueError(f"Cabinet {cabinet_id} not found")

            # Вызвать WB API
            wb_client = WildberriesAPIClient()
            cards = await wb_client.get_products(cabinet.api_token)

            log.info("sync_products_started", cabinet_id=cabinet_id, cards_count=len(cards))

            # Обработка карточек
            for card in cards:
                # Извлечь теги менеджера
                manager_tags = ','.join([tag.get('name', '') for tag in card.get('tags', [])])

                # Извлечь первый баркод
                barcode = None
                sizes = card.get('sizes', [])
                if sizes and sizes[0].get('skus'):
                    barcode = sizes[0]['skus'][0]

                # Первое фото
                image_url = None
                if card.get('mediaFiles'):
                    image_url = card['mediaFiles'][0]

                # Upsert продукт
                existing = await session.get(Product, card['nmID'])
                if existing:
                    existing.vendor_code = card.get('vendorCode')
                    existing.barcode = barcode
                    existing.title = card.get('object')
                    existing.manager = manager_tags
                    existing.image_url = image_url
                    existing.sizes = sizes
                    existing.last_update = datetime.utcnow()
                else:
                    product = Product(
                        nm_id=card['nmID'],
                        cabinet_id=cabinet_id,
                        vendor_code=card.get('vendorCode'),
                        barcode=barcode,
                        title=card.get('object'),
                        manager=manager_tags,
                        image_url=image_url,
                        sizes=sizes,
                        last_update=datetime.utcnow()
                    )
                    session.add(product)

            await session.commit()

            # Обновить статус на success
            await session.execute(
                update(SyncHistory)
                .where(SyncHistory.cabinet_id == cabinet_id, SyncHistory.sync_type == 'products')
                .values(status='success', error_message=None)
            )
            await session.commit()

            log.info("sync_products_completed", cabinet_id=cabinet_id)

        except Exception as e:
            log.error("sync_products_failed", cabinet_id=cabinet_id, error=str(e))
            await session.execute(
                update(SyncHistory)
                .where(SyncHistory.cabinet_id == cabinet_id, SyncHistory.sync_type == 'products')
                .values(status='failed', error_message=str(e))
            )
            await session.commit()
            raise self.retry(exc=e, countdown=60)

@shared_task(bind=True, max_retries=3)
async def sync_sales(self, cabinet_id: int, days_back: int = 90):
    """Синхронизация продаж и заказов за указанный период"""
    async with async_session() as session:
        try:
            await session.execute(
                update(SyncHistory)
                .where(SyncHistory.cabinet_id == cabinet_id, SyncHistory.sync_type == 'sales')
                .values(status='in_progress', last_sync_date=datetime.utcnow())
            )
            await session.commit()

            cabinet = await session.get(Cabinet, cabinet_id)
            if not cabinet:
                raise ValueError(f"Cabinet {cabinet_id} not found")

            # Дата начала
            date_from = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%S')

            wb_client = WildberriesAPIClient()

            # Получить заказы
            orders = await wb_client.get_orders(cabinet.api_token, date_from)

            # Получить продажи (выкупы)
            sales = await wb_client.get_sales(cabinet.api_token, date_from)

            log.info("sync_sales_started", cabinet_id=cabinet_id, orders=len(orders), sales=len(sales))

            # Агрегация по (nm_id, date)
            sales_dict = {}

            # Обработка заказов
            for order in orders:
                nm_id = order.get('nmId')
                date = datetime.fromisoformat(order.get('date').replace('Z', '+00:00')).date()
                key = (nm_id, date)

                if key not in sales_dict:
                    sales_dict[key] = {'orders': 0, 'buyouts': 0, 'revenue': 0}

                sales_dict[key]['orders'] += 1

            # Обработка продаж (выкупы)
            for sale in sales:
                nm_id = sale.get('nmId')
                date = datetime.fromisoformat(sale.get('date').replace('Z', '+00:00')).date()
                key = (nm_id, date)

                if key not in sales_dict:
                    sales_dict[key] = {'orders': 0, 'buyouts': 0, 'revenue': 0}

                # Проверка что это выкуп (не отмена)
                if sale.get('saleID') and not sale.get('cancelID'):
                    sales_dict[key]['buyouts'] += 1
                    sales_dict[key]['revenue'] += float(sale.get('priceWithDisc', 0))

            # Сохранение в БД (upsert)
            for (nm_id, date), metrics in sales_dict.items():
                # Проверить существование записи
                result = await session.execute(
                    select(SalesHistory).where(
                        SalesHistory.nm_id == nm_id,
                        SalesHistory.date == date
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    existing.orders_count = metrics['orders']
                    existing.buyouts_count = metrics['buyouts']
                    existing.revenue = metrics['revenue']
                else:
                    history = SalesHistory(
                        nm_id=nm_id,
                        cabinet_id=cabinet_id,
                        date=date,
                        orders_count=metrics['orders'],
                        buyouts_count=metrics['buyouts'],
                        revenue=metrics['revenue']
                    )
                    session.add(history)

            await session.commit()

            await session.execute(
                update(SyncHistory)
                .where(SyncHistory.cabinet_id == cabinet_id, SyncHistory.sync_type == 'sales')
                .values(status='success', error_message=None)
            )
            await session.commit()

            log.info("sync_sales_completed", cabinet_id=cabinet_id)

        except Exception as e:
            log.error("sync_sales_failed", cabinet_id=cabinet_id, error=str(e))
            await session.execute(
                update(SyncHistory)
                .where(SyncHistory.cabinet_id == cabinet_id, SyncHistory.sync_type == 'sales')
                .values(status='failed', error_message=str(e))
            )
            await session.commit()
            raise self.retry(exc=e, countdown=60)

@shared_task(bind=True, max_retries=3)
async def sync_stocks(self, cabinet_id: int):
    """Синхронизация остатков WB"""
    async with async_session() as session:
        try:
            await session.execute(
                update(SyncHistory)
                .where(SyncHistory.cabinet_id == cabinet_id, SyncHistory.sync_type == 'stocks')
                .values(status='in_progress', last_sync_date=datetime.utcnow())
            )
            await session.commit()

            cabinet = await session.get(Cabinet, cabinet_id)
            if not cabinet:
                raise ValueError(f"Cabinet {cabinet_id} not found")

            wb_client = WildberriesAPIClient()
            stocks = await wb_client.get_stocks(cabinet.api_token)

            log.info("sync_stocks_started", cabinet_id=cabinet_id, stocks_count=len(stocks))

            # Агрегация по nm_id
            stocks_dict = {}
            for stock in stocks:
                nm_id = stock.get('nmId')
                quantity = stock.get('quantity', 0)

                if nm_id not in stocks_dict:
                    stocks_dict[nm_id] = 0

                stocks_dict[nm_id] += quantity

            # Обновление products
            for nm_id, total_stock in stocks_dict.items():
                await session.execute(
                    update(Product)
                    .where(Product.nm_id == nm_id)
                    .values(stock_wb=total_stock, last_update=datetime.utcnow())
                )

            await session.commit()

            await session.execute(
                update(SyncHistory)
                .where(SyncHistory.cabinet_id == cabinet_id, SyncHistory.sync_type == 'stocks')
                .values(status='success', error_message=None)
            )
            await session.commit()

            log.info("sync_stocks_completed", cabinet_id=cabinet_id)

        except Exception as e:
            log.error("sync_stocks_failed", cabinet_id=cabinet_id, error=str(e))
            await session.execute(
                update(SyncHistory)
                .where(SyncHistory.cabinet_id == cabinet_id, SyncHistory.sync_type == 'stocks')
                .values(status='failed', error_message=str(e))
            )
            await session.commit()
            raise self.retry(exc=e, countdown=60)

# Задачи для синхронизации всех кабинетов
@shared_task
async def sync_all_products():
    """Синхронизация товаров для всех кабинетов"""
    async with async_session() as session:
        result = await session.execute(select(Cabinet))
        cabinets = result.scalars().all()

        for cabinet in cabinets:
            sync_products.delay(cabinet.id)

@shared_task
async def sync_all_sales():
    """Синхронизация продаж для всех кабинетов"""
    async with async_session() as session:
        result = await session.execute(select(Cabinet))
        cabinets = result.scalars().all()

        for cabinet in cabinets:
            sync_sales.delay(cabinet.id)

@shared_task
async def sync_all_stocks():
    """Синхронизация остатков для всех кабинетов"""
    async with async_session() as session:
        result = await session.execute(select(Cabinet))
        cabinets = result.scalars().all()

        for cabinet in cabinets:
            sync_stocks.delay(cabinet.id)
