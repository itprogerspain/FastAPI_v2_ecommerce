from fastapi import APIRouter, Depends, status

from app.application.categories.schemas import (
    Category as CategorySchema,
    CategoryCreate,
    CategoryUpdate,
)
from app.application.categories.service import CategoryService
from app.api.deps import get_category_service

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get(
    "/",
    response_model=list[CategorySchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(
    service: CategoryService = Depends(get_category_service),
):
    """
    Retrieve a complete list of all active product categories.
    """
    return service.get_all_categories()


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


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    """
    Update an existing category.

    Only name and parent_id can be modified.
    The category must be active.
    """
    return service.update_category(category_id, category_data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
):
    """
    Logically delete a category by setting is_active=False.
    """
    return service.delete_category(category_id)
