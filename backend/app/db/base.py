from backend.app.db.base_class import Base

# Import all models here so Alembic can discover them
from backend.app.models.user import User  # noqa
from backend.app.models.cabinet import Cabinet  # noqa
from backend.app.models.product import Product  # noqa
from backend.app.models.sales_history import SalesHistory  # noqa
from backend.app.models.sync_history import SyncHistory  # noqa
