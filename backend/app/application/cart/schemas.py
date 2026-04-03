from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from app.application.products.schemas import Product


class CartItemBase(BaseModel):
    """
    Base schema with shared fields for cart item input models.
    """

    product_id: int = Field(description="Product ID")
    quantity: int = Field(ge=1, description="Item quantity (minimum 1)")


class CartItemCreate(CartItemBase):
    """
    Schema for adding a new item to the cart.
    Used in POST /cart/items requests.

    Inherits product_id and quantity from CartItemBase.
    Separated from CartItemBase to allow future extensions
    (e.g. replace_quantity: bool) without affecting other models.
    """

    pass


class CartItemUpdate(BaseModel):
    """
    Schema for updating item quantity in the cart.
    Used in PUT /cart/items/{product_id} requests.

    product_id is passed via URL path, not request body.
    Only quantity can be changed.
    """

    quantity: int = Field(..., ge=1, description="New item quantity (minimum 1)")


class CartItem(BaseModel):
    """
    Schema for returning a single cart item with full product details.
    Used in GET /cart/ responses.
    """

    id: int = Field(..., description="Cart item record ID")
    quantity: int = Field(..., ge=1, description="Item quantity")
    product: Product = Field(..., description="Full product information")

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    """
    Schema for returning the full cart of the current user.
    Used in GET /cart/ responses.
    """

    user_id: int = Field(..., description="Cart owner user ID")
    items: list[CartItem] = Field(
        default_factory=list, description="List of cart items"
    )
    total_quantity: int = Field(..., ge=0, description="Total number of items")
    total_price: Decimal = Field(..., ge=0, description="Total price of all items")

    model_config = ConfigDict(from_attributes=True)
