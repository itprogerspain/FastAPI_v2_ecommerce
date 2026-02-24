from fastapi import APIRouter, Depends, status

from app.application.products.schemas import (
    Product as ProductSchema,
    ProductCreate,
)
from app.application.products.service import ProductService
from app.api.deps import get_product_service

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.post(
    "/",
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    """
    Create a new product.
    """
    return service.create_product(product_data)


@router.get(
    "/",
    response_model=list[ProductSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_products(
    service: ProductService = Depends(get_product_service),
):
    """
    Retrieve all active products.
    """
    return service.get_all_products()


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
    Retrieve active products by category.
    """
    return service.get_products_by_category(category_id)


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
    Retrieve a single active product.
    """
    return service.get_product(product_id)


@router.put(
    "/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: int,
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    """
    Update an existing product.
    """
    return service.update_product(product_id, product_data)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    """
    Logically delete a product by setting is_active=False.
    """
    return service.delete_product(product_id)
