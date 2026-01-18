from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from cryptography.fernet import Fernet
from app.db.session import get_db
from app.models import Cabinet, User, Product
from app.schemas.settings import CabinetCreate, CabinetResponse, UserCreate, UserUpdate, UserResponse
from app.core.dependencies import get_current_user, require_role
from app.core.security import get_password_hash
from app.services.wb_api import WildberriesAPIClient
from app.models.user import User as UserModel
import os

router = APIRouter(prefix="/settings", tags=["settings"])

# Ключ шифрования для API токенов (должен быть в config)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

# ========== CABINETS ==========

@router.get("/cabinets", response_model=List[CabinetResponse])
async def get_cabinets(
    current_user: UserModel = Depends(require_role(['admin', 'leader'])),
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех кабинетов"""
    result = await db.execute(select(Cabinet))
    cabinets = result.scalars().all()

    return [
        CabinetResponse(
            id=cab.id,
            name=cab.name,
            created_at=cab.created_at
        ) for cab in cabinets
    ]

@router.post("/cabinets", response_model=CabinetResponse)
async def create_cabinet(
    cabinet_data: CabinetCreate,
    current_user: UserModel = Depends(require_role(['admin'])),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый кабинет с проверкой токена"""

    # Проверка валидности токена через WB API
    wb_client = WildberriesAPIClient()
    try:
        # Тестовый запрос
        await wb_client.get_stocks(cabinet_data.api_token)
    except Exception as e:
        raise HTTPException(400, detail=f"Неверный API токен: {str(e)}")

    # Шифрование токена
    encrypted_token = fernet.encrypt(cabinet_data.api_token.encode()).decode()

    # Создание кабинета
    cabinet = Cabinet(
        name=cabinet_data.name,
        api_token=encrypted_token
    )

    db.add(cabinet)
    await db.commit()
    await db.refresh(cabinet)

    return CabinetResponse(
        id=cabinet.id,
        name=cabinet.name,
        created_at=cabinet.created_at
    )

@router.put("/cabinets/{cabinet_id}", response_model=CabinetResponse)
async def update_cabinet(
    cabinet_id: int,
    cabinet_data: CabinetCreate,
    current_user: UserModel = Depends(require_role(['admin'])),
    db: AsyncSession = Depends(get_db)
):
    """Обновить кабинет"""
    cabinet = await db.get(Cabinet, cabinet_id)
    if not cabinet:
        raise HTTPException(404, detail="Cabinet not found")

    # Если токен изменился - проверить его
    if cabinet_data.api_token:
        wb_client = WildberriesAPIClient()
        try:
            await wb_client.get_stocks(cabinet_data.api_token)
            encrypted_token = fernet.encrypt(cabinet_data.api_token.encode()).decode()
            cabinet.api_token = encrypted_token
        except Exception as e:
            raise HTTPException(400, detail=f"Неверный API токен: {str(e)}")

    cabinet.name = cabinet_data.name
    await db.commit()
    await db.refresh(cabinet)

    return CabinetResponse(
        id=cabinet.id,
        name=cabinet.name,
        created_at=cabinet.created_at
    )

@router.delete("/cabinets/{cabinet_id}")
async def delete_cabinet(
    cabinet_id: int,
    current_user: UserModel = Depends(require_role(['admin'])),
    db: AsyncSession = Depends(get_db)
):
    """Удалить кабинет"""
    cabinet = await db.get(Cabinet, cabinet_id)
    if not cabinet:
        raise HTTPException(404, detail="Cabinet not found")

    await db.delete(cabinet)
    await db.commit()

    return {"message": "Cabinet deleted successfully"}

# ========== USERS ==========

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    current_user: UserModel = Depends(require_role(['admin'])),
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех пользователей"""
    result = await db.execute(select(User))
    users = result.scalars().all()

    return [
        UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            allowed_tags=user.allowed_tags,
            created_at=user.created_at
        ) for user in users
    ]

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: UserModel = Depends(require_role(['admin'])),
    db: AsyncSession = Depends(get_db)
):
    """Создать нового пользователя"""

    # Проверка уникальности email
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(400, detail="Email already registered")

    # Валидация: для менеджера обязательно allowed_tags
    if user_data.role == 'manager' and not user_data.allowed_tags:
        raise HTTPException(400, detail="Manager must have allowed_tags")

    # Создание пользователя
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        allowed_tags=user_data.allowed_tags if user_data.role == 'manager' else None
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        allowed_tags=user.allowed_tags,
        created_at=user.created_at
    )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: UserModel = Depends(require_role(['admin'])),
    db: AsyncSession = Depends(get_db)
):
    """Обновить пользователя"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, detail="User not found")

    # Обновление полей
    if user_data.name:
        user.name = user_data.name
    if user_data.email:
        user.email = user_data.email
    if user_data.password:
        user.password_hash = get_password_hash(user_data.password)
    if user_data.role:
        user.role = user_data.role

    # allowed_tags только для менеджеров
    if user_data.role == 'manager':
        user.allowed_tags = user_data.allowed_tags
    else:
        user.allowed_tags = None

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        allowed_tags=user.allowed_tags,
        created_at=user.created_at
    )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserModel = Depends(require_role(['admin'])),
    db: AsyncSession = Depends(get_db)
):
    """Удалить пользователя"""

    # Нельзя удалить самого себя
    if user_id == current_user.id:
        raise HTTPException(400, detail="Cannot delete yourself")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"message": "User deleted successfully"}

# ========== INTEGRATIONS ==========

@router.post("/integrations/excel-upload")
async def upload_excel(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(require_role(['admin', 'leader'])),
    db: AsyncSession = Depends(get_db)
):
    """Загрузить Excel файл с остатками"""

    # Валидация расширения
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, detail="Only .xlsx or .xls files allowed")

    # Сохранение временного файла
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        # Парсинг Excel
        import pandas as pd
        df = pd.read_excel(temp_path)

        # Валидация колонок
        required_cols = ['Артикул продавца', 'Остаток склад']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise HTTPException(400, detail=f"Missing columns: {', '.join(missing)}")

        # Очистка данных
        df = df.dropna(subset=['Артикул продавца'])
        df['Остаток склад'] = pd.to_numeric(df['Остаток склад'], errors='coerce').fillna(0).astype(int)

        # Обновление products
        updated_count = 0
        for _, row in df.iterrows():
            vendor_code = row['Артикул продавца']
            stock = int(row['Остаток склад'])

            result = await db.execute(
                select(Product).where(Product.vendor_code == vendor_code)
            )
            product = result.scalar_one_or_none()

            if product:
                product.stock_own = stock
                updated_count += 1

        await db.commit()

        return {
            "success": True,
            "processed_count": updated_count,
            "total_rows": len(df)
        }

    except Exception as e:
        raise HTTPException(400, detail=f"Error processing file: {str(e)}")
    finally:
        # Удалить временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_settings():
    return {"message": "Settings route"}
