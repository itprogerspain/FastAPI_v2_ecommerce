from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    """
    Schema for creating or updating a category.
    Used in POST and PUT requests.
    """

    name: str = Field(
        ..., min_length=3, max_length=50, description="Category name (3–50 characters)"
    )
    parent_id: int | None = Field(None, description="Parent category ID, if applicable")


class CategoryUpdate(CategoryCreate):
    """
    Schema for updating a category.
    Used in PUT requests.
    Inherits validation rules from CategoryCreate.
    """

    pass


class Category(CategoryCreate):
    """
    Schema for returning category data.
    Used in GET responses.
    """

    id: int = Field(..., description="Unique category identifier")
    is_active: bool = Field(..., description="Indicates whether the category is active")

    model_config = ConfigDict(from_attributes=True)
