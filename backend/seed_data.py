import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

sys.path.append(os.getcwd())

from app.db.session import async_session, engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.cabinet import Cabinet
from app.models.product import Product
from app.models.sales_history import SalesHistory
from passlib.context import CryptContext
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Check if user exists
        stmt = select(User).where(User.email == "admin@example.com")
        result = await session.execute(stmt)
        if result.scalars().first():
            print("Data already seeded (User found). Skipping user creation.")
            # We might still want to seed sales history if missing
        else:
            # User
            user = User(
                email="admin@example.com",
                password_hash=pwd_context.hash("password"),
                role=UserRole.admin,
                name="Admin User",
                allowed_tags=""
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

            # Cabinet
            cabinet = Cabinet(
                user_id=user.id,
                name="Main Cabinet",
                api_token="encrypted_token_placeholder",
                is_active=1
            )
            session.add(cabinet)
            await session.commit()
            await session.refresh(cabinet)

            # Products
            products = [
                Product(nm_id=100004, cabinet_id=cabinet.id, vendor_code="ART-104", barcode="460000000104", title="Product A", orders=288, sales=165, revenue=199029, stock_wb=100),
                Product(nm_id=100006, cabinet_id=cabinet.id, vendor_code="ART-106", barcode="460000000106", title="Product B", orders=236, sales=152, revenue=212185, stock_wb=50),
                Product(nm_id=100008, cabinet_id=cabinet.id, vendor_code="ART-108", barcode="460000000108", title="Product C", orders=283, sales=140, revenue=148639, stock_wb=5)
            ]
            for p in products:
                session.add(p)

            await session.commit()
            print("Users, Cabinets, Products seeded.")

        # Seed Sales History for the last 30 days
        # First, get products
        stmt = select(Product)
        result = await session.execute(stmt)
        products = result.scalars().all()

        if not products:
             print("No products found to seed history for.")
             return

        today = datetime.utcnow().date()

        # Check if we already have history to avoid duplicates
        # Simplified: just delete old history for these products? No, let's just add if not exists.
        # For simplicity in this dev script, let's just clear history and re-seed.

        # await session.execute("DELETE FROM sales_history") # Raw SQL might be tricky with asyncpg/sqlite differences
        # Let's just generate for days that don't exist? Too complex.
        # Let's just add data. If it fails on constraint (nm_id, date) unique, we skip.

        print("Seeding Sales History...")
        for product in products:
            for i in range(30):
                date = today - timedelta(days=i)

                # Check exist
                # stmt = select(SalesHistory).where(SalesHistory.nm_id == product.nm_id, SalesHistory.date == date)
                # res = await session.execute(stmt)
                # if res.scalars().first():
                #    continue

                # Generate random stats
                orders = random.randint(0, 20)
                sales = random.randint(0, orders)
                revenue = sales * 1000.0 # Approx price

                history = SalesHistory(
                    nm_id=product.nm_id,
                    cabinet_id=product.cabinet_id,
                    date=date,
                    orders_count=orders,
                    buyouts_count=sales,
                    revenue=revenue
                )
                session.add(history)

        try:
            await session.commit()
            print("Sales History seeded.")
        except Exception as e:
            print(f"Error seeding history (probably duplicates): {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(seed())
