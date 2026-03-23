from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    """
    Schema for creating a review.
    Used in POST /reviews/ requests.
    Only buyers can create reviews.
    """

    product_id: int = Field(..., description="ID of the product being reviewed")
    comment: str | None = Field(None, description="Optional review comment")
    grade: int = Field(..., ge=1, le=5, description="Rating grade from 1 to 5")


class Review(BaseModel):
    """
    Schema for returning review data in API responses.
    """

    id: int
    user_id: int
    product_id: int
    comment: str | None
    comment_date: datetime
    grade: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
