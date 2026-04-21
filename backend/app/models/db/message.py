from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db import Base

if TYPE_CHECKING:
    from app.models.db.user import User


class Message(Base):
    """
    Chat message model — persists WebSocket chat history to the database.

    Supports two chat types:
        1. Buyer ↔ Seller : both sender_id and receiver_id are set,
                            product_id is optionally set for product-related questions.
        2. Support chat   : sender_id is the user, receiver_id is None
                            (support agent is identified by role, not a fixed user).

    Messages are soft-deleted (is_active=False) rather than hard-deleted
    to preserve chat history for dispute resolution and auditing.
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # The user who sent the message
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The user who receives the message.
    # None for support chat — support agents are identified by role.
    receiver_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Optional link to a product — used in buyer ↔ seller chats about a specific item
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    text: Mapped[str] = mapped_column(String(2000), nullable=False)

    # True once the receiver has read the message — used for unread badge counts
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Soft delete — preserves history for auditing and dispute resolution
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamp set at DB level in UTC
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -------------------------
    # Relationships
    # -------------------------

    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages",
    )
    receiver: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_messages",
    )
