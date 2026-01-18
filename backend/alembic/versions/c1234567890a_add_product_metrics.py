"""Add product metrics (orders, sales, revenue)

Revision ID: c1234567890a
Revises: b0891cbec318
Create Date: 2026-01-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1234567890a'
down_revision: Union[str, None] = 'b0891cbec318'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавить новые колонки метрик в таблицу products
    op.add_column('products', sa.Column('orders', sa.Integer(), nullable=True, server_default='0', comment='Количество заказов'))
    op.add_column('products', sa.Column('sales', sa.Integer(), nullable=True, server_default='0', comment='Выкупы'))
    op.add_column('products', sa.Column('revenue', sa.Numeric(precision=12, scale=2), nullable=True, server_default='0.0', comment='Выручка (рубли)'))
    op.add_column('products', sa.Column('updated_at', sa.DateTime(), nullable=True, comment='Время последнего обновления'))


def downgrade() -> None:
    op.drop_column('products', 'updated_at')
    op.drop_column('products', 'revenue')
    op.drop_column('products', 'sales')
    op.drop_column('products', 'orders')
