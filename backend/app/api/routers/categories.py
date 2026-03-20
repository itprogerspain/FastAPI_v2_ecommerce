from fastapi import APIRouter, Depends, status

from app.application.categories.schemas import (
    Category as CategorySchema,
    CategoryCreate,
    CategoryUpdate,
)
from app.application.categories.service import CategoryService
from app.api.deps import get_category_service
from app.core.deps import get_current_admin
from app.models.db.user import User as UserModel

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


# -------------------------
# Public endpoints (no auth required)
# -------------------------


@router.get(
    "/",
    response_model=list[CategorySchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(
    service: CategoryService = Depends(get_category_service),
):
    """
    Retrieve a complete list of all active product categories (public).
    """
    return await service.get_all_categories()


# -------------------------
# Protected endpoints (admin only)
# -------------------------


@router.post(
    "/",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
    current_user: UserModel = Depends(get_current_admin),
):
    """
    Create a new category (admin only).
    """
    return await service.create_category(category)


@router.put(
    "/{category_id}",
    response_model=CategorySchema,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
    current_user: UserModel = Depends(get_current_admin),
):
    """
    Update an existing category (admin only).
    """
    return await service.update_category(category_id, category_data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
    current_user: UserModel = Depends(get_current_admin),
):
    """
    Logically delete a category by setting is_active=False (admin only).
    """
    return await service.delete_category(category_id)
