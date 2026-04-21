from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ProfileUpdate(BaseModel):
    """
    Schema for updating the current user's profile.
    All fields are optional — the client sends only what changed.
    """

    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=20)
    bio: str | None = Field(None, max_length=500)

    # Delivery address
    country: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=100)
    street: str | None = Field(None, max_length=200)
    postal_code: str | None = Field(None, max_length=20)

    # Seller-specific fields — ignored for buyers on the frontend,
    # but no server-side restriction enforced here (kept simple).
    shop_name: str | None = Field(None, max_length=100)
    shop_description: str | None = Field(None, max_length=1000)


class Profile(BaseModel):
    """
    Schema for returning profile data in API responses.
    avatar_url is included but updated via a dedicated upload endpoint.
    """

    id: int
    user_id: int
    first_name: str | None
    last_name: str | None
    phone: str | None
    avatar_url: str | None
    bio: str | None
    country: str | None
    city: str | None
    street: str | None
    postal_code: str | None
    shop_name: str | None
    shop_description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
