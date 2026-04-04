from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from app.application.products.schemas import Product


class OrderItem(BaseModel):
    """
    Schema for a single order line item.
    Prices are fixed at the moment of purchase and do not change.
    """

    id: int = Field(..., description="Order item ID")
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    unit_price: Decimal = Field(
        ..., ge=0, description="Price per unit at time of purchase"
    )
    total_price: Decimal = Field(
        ..., ge=0, description="Total price for this line item"
    )
    product: Product | None = Field(None, description="Full product details")

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    """
    Full order representation.
    Used in create, get single and list responses.
    """

    id: int = Field(..., description="Order ID")
    user_id: int = Field(..., description="Owner user ID")
    status: str = Field(..., description="Current order status")
    total_amount: Decimal = Field(..., ge=0, description="Total order amount")
    created_at: datetime = Field(..., description="When the order was created")
    updated_at: datetime = Field(..., description="When the order was last updated")
    items: list[OrderItem] = Field(default_factory=list, description="Order line items")

    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    """
    Paginated list of orders.
    Returned by GET /orders/ endpoint.
    """

    items: list[Order] = Field(..., description="Orders on the current page")
    total: int = Field(ge=0, description="Total number of orders")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, description="Page size")

    model_config = ConfigDict(from_attributes=True)
