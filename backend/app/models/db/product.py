from typing import TYPE_CHECKING

from decimal import Decimal

from sqlalchemy import String, Boolean, Integer, Numeric, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.infrastructure.db import Base

if TYPE_CHECKING:
    from app.models.db.category import Category
    from app.models.db.user import User
    from app.models.db.review import Review


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )  # Average review grade
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True
    )
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    seller: Mapped["User"] = relationship("User", back_populates="products")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="product")
