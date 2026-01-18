from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.routes import auth
from app.db.session import engine, Base, async_session
from app.models import User
from app.core.security import get_password_hash
from sqlalchemy.future import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == "user@example.com"))
        user = result.scalars().first()
        if not user:
            user = User(
                email="user@example.com",
                hashed_password=get_password_hash("password"),
                name="Test User",
                role="admin",
                allowed_tags="tag1,tag2"
            )
            session.add(user)
            await session.commit()
            print("Created test user: user@example.com / password")

    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Hello World"}
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import auth_router, dashboard_router, settings_router

app = FastAPI(title="Wildberries Analytics Electra API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["settings"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
