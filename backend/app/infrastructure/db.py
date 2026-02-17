from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# Database connection string for SQLite
DATABASE_URL = "sqlite:///./db/ecommerce.db"

# Create the SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},  # Required for SQLite
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    """

    pass


# Dynamically import all models so SQLAlchemy can see them
import importlib
import pkgutil
from app.models import db as models_db  # points to your models/db folder

for loader, module_name, is_pkg in pkgutil.iter_modules(models_db.__path__):
    importlib.import_module(f"app.models.db.{module_name}")


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session per request.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
