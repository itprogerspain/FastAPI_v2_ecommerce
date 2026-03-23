from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db import Base

if TYPE_CHECKING:
    from app.models.db.user import User
    from app.models.db.product import Product


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    grade: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="reviews")
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
