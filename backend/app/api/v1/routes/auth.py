from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from backend.app.core.dependencies import get_db, get_current_user
from backend.app.models import User
from backend.app.schemas.user import TokenResponse, UserResponse

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Check email exists
    # In OAuth2PasswordRequestForm, username field holds the email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Payload for access token
    access_token_payload = {
        "sub": str(user.id),
        "role": user.role,
        "tags": user.allowed_tags
    }

    access_token = await create_access_token(data=access_token_payload)

    # Payload for refresh token
    refresh_token_payload = {"sub": str(user.id)}
    refresh_token = await create_refresh_token(data=refresh_token_payload)

    # Set httpOnly cookie with refresh_token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False, # Should be True in production (HTTPS)
        samesite="lax",
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token_endpoint(
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = await verify_token(refresh_token)
    user_id = payload.get("sub")

    if not user_id:
         raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token_payload = {
        "sub": str(user.id),
        "role": user.role,
        "tags": user.allowed_tags
    }

    access_token = await create_access_token(data=access_token_payload)

    return {"access_token": access_token}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_auth():
    return {"message": "Auth route"}
