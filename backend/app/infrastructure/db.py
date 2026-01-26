from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database connection string for SQLite
DATABASE_URL = "sqlite:///./db/ecommerce2.db"

# Create the SQLAlchemy Engine
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

# # на будущее
#
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
# from fastapi import Depends
#
# # Database connection string for SQLite
# DATABASE_URL = "sqlite:///./db/ecommerce2.db"
#
# # Create the SQLAlchemy Engine
# engine = create_engine(
#     DATABASE_URL,
#     echo=True,
#     connect_args={"check_same_thread": False}  # нужен для SQLite
# )
#
# # Create a configured "Session" class
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# # Base class for declarative models (SQLAlchemy 2.0 style)
# class Base(DeclarativeBase):
#     pass
#
# # Dependency to get DB session for FastAPI
# def get_db() -> Session:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

