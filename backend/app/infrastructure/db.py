from typing import Generator, AsyncGenerator
from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.infrastructure.base import Base

# -------------------- LOAD ENVIRONMENT VARIABLES --------------------
load_dotenv()


# -------------------- SYNCHRONOUS CONNECTION (SQLite) --------------------
DATABASE_URL = "sqlite:///./db/ecommerce.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# class Base(DeclarativeBase):
#     """Base class for all ORM models."""
#
#     pass


# -------------------- DYNAMIC MODEL IMPORT --------------------
import importlib
import pkgutil
from app.models import db as models_db

for loader, module_name, is_pkg in pkgutil.iter_modules(models_db.__path__):
    importlib.import_module(f"app.models.db.{module_name}")


def get_db() -> Generator[Session, None, None]:
    """Provide a synchronous database session per request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------- ASYNCHRONOUS CONNECTION (PostgreSQL) --------------------
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
)

async_session_maker = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an asynchronous database session per request."""
    async with async_session_maker() as session:
        yield session
