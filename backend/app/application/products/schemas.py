from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    """
    Schema for creating or updating a product.
    Used in POST and PUT requests.
    """

    name: str = Field(
        ..., min_length=3, max_length=100, description="Product name (3–100 characters)"
    )
    description: str | None = Field(
        None, max_length=500, description="Product description (up to 500 characters)"
    )
    price: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Product price (must be greater than 0)",
    )
    stock: int = Field(..., ge=0, description="Number of items in stock (0 or more)")
    category_id: int = Field(
        ..., description="ID of the category this product belongs to"
    )

    model_config = ConfigDict(from_attributes=True, json_encoders={Decimal: float})


class Product(ProductCreate):
    """
    Schema for returning product data.
    Used in GET responses.
    """

    id: int = Field(..., description="Unique product identifier")
    is_active: bool = Field(..., description="Indicates whether the product is active")
    rating: float = Field(..., description="Average rating based on reviews")
    image_url: str | None = Field(None, description="Product image URL")

    model_config = ConfigDict(from_attributes=True, json_encoders={Decimal: float})


class ProductList(BaseModel):
    """
    Paginated response schema for product listings.
    """

    items: list[Product] = Field(description="Products for the current page")
    total: int = Field(ge=0, description="Total number of active products")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, description="Number of items per page")

    model_config = ConfigDict(from_attributes=True)
