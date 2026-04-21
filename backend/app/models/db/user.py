from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db import Base

if TYPE_CHECKING:
    from app.models.db.product import Product
    from app.models.db.review import Review
    from app.models.db.cart import CartItem
    from app.models.db.order import Order
    from app.models.db.profile import Profile
    from app.models.db.message import Message


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(
        String, default="buyer"
    )  # "buyer", "seller" or "admin"

    products: Mapped[list["Product"]] = relationship("Product", back_populates="seller")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user")
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan"
    )
    # Messages sent and received by this user.
    # Two separate relationships because Message has two FK pointing to users:
    # sender_id and receiver_id — SQLAlchemy requires foreign_keys to be explicit.
    sent_messages: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_messages: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        back_populates="receiver",
    )

    # One-to-one: each user has at most one profile.
    # uselist=False tells SQLAlchemy to return a single object, not a list.
    # cascade ensures profile is deleted when user is deleted.
    profile: Mapped["Profile | None"] = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
