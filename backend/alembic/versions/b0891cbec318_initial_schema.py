"""Initial schema

Revision ID: b0891cbec318
Revises:
Create Date: 2024-05-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0891cbec318'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'leader', 'manager', name='userrole'), nullable=False),
        sa.Column('allowed_tags', sa.String(length=500), nullable=True, comment='Теги через запятую для менеджеров'),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Cabinets
    op.create_table('cabinets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Название ИП'),
        sa.Column('api_token', sa.Text(), nullable=False, comment='Зашифрованный токен WB'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Products
    op.create_table('products',
        sa.Column('nm_id', sa.BigInteger(), nullable=False, comment='Артикул WB'),
        sa.Column('cabinet_id', sa.Integer(), nullable=False),
        sa.Column('vendor_code', sa.String(length=100), nullable=True, comment='Артикул продавца'),
        sa.Column('barcode', sa.String(length=50), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('manager', sa.String(length=255), nullable=True, comment='Теги менеджера из WB'),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('stock_wb', sa.Integer(), nullable=True, comment='Остаток на WB'),
        sa.Column('stock_own', sa.Integer(), nullable=True, comment='Остаток своего склада'),
        sa.Column('last_update', sa.DateTime(), nullable=True),
        sa.Column('sizes', sa.JSON(), nullable=True, comment='Массив размеров с баркодами'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cabinet_id'], ['cabinets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('nm_id')
    )
    op.create_index(op.f('ix_products_vendor_code'), 'products', ['vendor_code'], unique=False)
    op.create_index(op.f('ix_products_manager'), 'products', ['manager'], unique=False)
    op.create_index('idx_product_cabinet_manager', 'products', ['cabinet_id', 'manager'], unique=False)

    # SalesHistory
    op.create_table('sales_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nm_id', sa.BigInteger(), nullable=False),
        sa.Column('cabinet_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('orders_count', sa.Integer(), nullable=True),
        sa.Column('buyouts_count', sa.Integer(), nullable=True),
        sa.Column('revenue', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cabinet_id'], ['cabinets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['nm_id'], ['products.nm_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nm_id', 'date', name='uq_sales_nm_date')
    )
    op.create_index('idx_sales_nm_date', 'sales_history', ['nm_id', 'date'], unique=False)
    op.create_index('idx_sales_cabinet_date', 'sales_history', ['cabinet_id', 'date'], unique=False)

    # SyncHistory
    op.create_table('sync_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cabinet_id', sa.Integer(), nullable=False),
        sa.Column('sync_type', sa.Enum('stocks', 'sales', 'orders', 'products', name='synctype'), nullable=False),
        sa.Column('last_sync_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('success', 'failed', 'in_progress', name='syncstatus'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cabinet_id'], ['cabinets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sync_cabinet_type', 'sync_history', ['cabinet_id', 'sync_type'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_sync_cabinet_type', table_name='sync_history')
    op.drop_table('sync_history')
    op.execute("DROP TYPE IF EXISTS syncstatus")
    op.execute("DROP TYPE IF EXISTS synctype")

    op.drop_index('idx_sales_cabinet_date', table_name='sales_history')
    op.drop_index('idx_sales_nm_date', table_name='sales_history')
    op.drop_table('sales_history')

    op.drop_index('idx_product_cabinet_manager', table_name='products')
    op.drop_index(op.f('ix_products_manager'), table_name='products')
    op.drop_index(op.f('ix_products_vendor_code'), table_name='products')
    op.drop_table('products')

    op.drop_table('cabinets')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS userrole")
