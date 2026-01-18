from app.db.base_class import Base

# Import all models here so Alembic can discover them
from app.models.user import User  # noqa
from app.models.cabinet import Cabinet  # noqa
from app.models.product import Product  # noqa
from app.models.sales_history import SalesHistory  # noqa
from app.models.sync_history import SyncHistory  # noqa
