from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.routes import auth, products
from app.db.session import engine, Base, async_session
from app.models import User
from app.core.security import get_password_hash
from sqlalchemy.future import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # Shutdown

app = FastAPI(title="Wildberries Analytics Electra API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])

@app.get("/")
async def root():
    return {"message": "Electra Analytics API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
