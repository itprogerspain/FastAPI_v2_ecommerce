from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class MessageCreate(BaseModel):
    """
    Schema for sending a new message.

    receiver_id is None for support chat — support agents are identified
    by role, not by a fixed user ID.
    product_id is optional — only set when the message is about a specific product.
    """

    receiver_id: int | None = Field(None, description="Recipient user ID. None for support chat.")
    product_id: int | None = Field(None, description="Optional product reference.")
    text: str = Field(..., min_length=1, max_length=2000)


class MessageOut(BaseModel):
    """
    Schema for returning a message in API responses.
    """

    id: int
    sender_id: int
    receiver_id: int | None
    product_id: int | None
    text: str
    is_read: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageList(BaseModel):
    """
    Paginated list of messages (used for conversation history).
    """

    items: list[MessageOut]
    total: int
    page: int
    page_size: int


class UnreadCount(BaseModel):
    """
    Unread message count — returned for the notification badge.
    """

    unread_count: int
