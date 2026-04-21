from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db import Base

if TYPE_CHECKING:
    from app.models.db.user import User


class Profile(Base):
    """
    Extended user profile — one-to-one with User.

    Separated from User intentionally:
        - User holds only auth-critical data (email, password, role)
        - Profile holds personal and delivery info that can be updated freely
        - Keeps the users table lean and focused on authentication

    All personal fields are optional — users are not forced to fill
    them on registration. They can be completed later in account settings.
    """

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)

    # One-to-one link to User.
    # unique=True enforces the one-to-one constraint at the database level.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # -------------------------
    # Personal info
    # -------------------------

    first_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Phone stored as string to support international formats (+7, +1, etc.)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Avatar stored as a relative URL via our media/ upload system (e.g. /media/avatars/uuid.jpg)
    # TODO: create media/avatars/ directory and upload endpoint when implementing profile editing
    avatar_url: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Short bio — useful for sellers to describe themselves to buyers
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # -------------------------
    # Delivery address
    # -------------------------
    # Stored flat (not a separate table) for simplicity.
    # TODO: extract into a separate Address model if multiple addresses per user are needed

    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    street: Mapped[str | None] = mapped_column(String(200), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # -------------------------
    # Seller-specific fields
    # -------------------------
    # Only relevant when user.role == "seller", ignored for buyers.
    # Displayed on the seller's public storefront page.

    shop_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shop_description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # -------------------------
    # Timestamps
    # -------------------------
    # Both set at DB level in UTC for consistency across timezones.

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # -------------------------
    # Relationships
    # -------------------------

    user: Mapped["User"] = relationship("User", back_populates="profile")
