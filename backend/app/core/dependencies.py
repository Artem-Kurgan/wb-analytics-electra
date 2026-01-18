from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.security import verify_token
from app.db.session import get_db
from app.models import User, Product

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Извлекает текущего пользователя из JWT токена"""
    payload = await verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
         raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID in token")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user

def require_role(allowed_roles: List[str]):
    """Декоратор для проверки роли пользователя"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(403, "Insufficient permissions")
        return current_user
    return role_checker

async def filter_by_user_tags(
    products: List[Product],
    current_user: User
) -> List[Product]:
    """Фильтрует товары по тегам менеджера"""
    if current_user.role in ['admin', 'leader']:
        return products

    user_tags = [tag.strip() for tag in (current_user.allowed_tags or "").split(",") if tag.strip()]
    return [p for p in products if p.manager in user_tags]
