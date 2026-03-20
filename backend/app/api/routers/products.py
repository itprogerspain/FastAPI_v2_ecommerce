from fastapi import APIRouter, Depends, status

from app.application.products.schemas import (
    Product as ProductSchema,
    ProductCreate,
)
from app.application.products.service import ProductService
from app.api.deps import get_product_service
from app.core.deps import get_current_seller
from app.models.db.user import User as UserModel

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


# -------------------------
# Public endpoints (no auth required)
# -------------------------


@router.get(
    "/",
    response_model=list[ProductSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_products(
    service: ProductService = Depends(get_product_service),
):
    """
    Retrieve all active products (public).
    """
    return await service.get_all_products()


@router.get(
    "/category/{category_id}",
    response_model=list[ProductSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: int,
    service: ProductService = Depends(get_product_service),
):
    """
    Retrieve active products by category (public).
    """
    return await service.get_products_by_category(category_id)


@router.get(
    "/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    """
    Retrieve a single active product (public).
    """
    return await service.get_product(product_id)


# -------------------------
# Protected endpoints (seller only)
# -------------------------


@router.post(
    "/",
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service),
    current_user: UserModel = Depends(get_current_seller),
):
    """
    Create a new product bound to the current seller (seller only).
    """
    return await service.create_product(product_data, seller_id=current_user.id)


@router.put(
    "/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: int,
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service),
    current_user: UserModel = Depends(get_current_seller),
):
    """
    Update a product. Only the owning seller can update it (seller only).
    """
    return await service.update_product(
        product_id, product_data, seller_id=current_user.id
    )


@router.delete(
    "/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
    current_user: UserModel = Depends(get_current_seller),
):
    """
    Logically delete a product. Only the owning seller can delete it (seller only).
    """
    return await service.delete_product(product_id, seller_id=current_user.id)
