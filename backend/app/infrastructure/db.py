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


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session per request.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
