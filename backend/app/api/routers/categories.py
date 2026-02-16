from fastapi import APIRouter, Depends, status

from app.application.categories.schemas import (
    Category as CategorySchema,
    CategoryCreate,
)
from app.application.categories.service import CategoryService
from app.api.deps import get_category_service

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/")
async def get_all_categories():
    """
    Retrieve a complete list of all product categories.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder for actual category list
        "message": "Retrieved all categories successfully (stub)",
    }


@router.post(
    "/",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    """
    Create a new category.
    """

    return service.create_category(category)


@router.put("/{category_id}")
async def update_category(category_id: int):
    """
    Update the details of a category by its ID.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder for the updated category
        "message": f"Category with ID {category_id} updated successfully (stub)",
    }


@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """
    Delete a category by its ID.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder since category is deleted
        "message": f"Category with ID {category_id} deleted successfully (stub)",
    }
