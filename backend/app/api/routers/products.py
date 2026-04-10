import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status

from app.application.products.schemas import (
    Product as ProductSchema,
    ProductCreate,
    ProductList,
)
from app.application.products.service import ProductService
from app.application.reviews.schemas import Review as ReviewSchema
from app.application.reviews.service import ReviewService
from app.api.deps import get_product_service, get_review_service
from app.core.deps import get_current_seller
from app.models.db.user import User as UserModel

# TODO: For production with large file volumes, replace local media storage with
#       S3-compatible storage (e.g. AWS S3, MinIO) or a CDN.
#       Local storage is acceptable for learning/pet projects only.

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MEDIA_ROOT = BASE_DIR / "media" / "products"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 097 152 bites


async def save_product_image(file: UploadFile) -> str:
    """
    Saves the product image and returns a relative URL.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Only JPG, PNG or WebP images are allowed"
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Image is too large")

    extension = Path(file.filename or "").suffix.lower() or ".jpg"
    file_name = f"{uuid.uuid4()}{extension}"
    file_path = MEDIA_ROOT / file_name
    file_path.write_bytes(content)

    return f"/media/products/{file_name}"


def remove_product_image(url: str | None) -> None:
    """
    Deletes the image file if it exists.
    """
    if not url:
        return
    relative_path = url.lstrip("/")
    file_path = BASE_DIR / relative_path
    if file_path.exists():
        file_path.unlink()


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


# -------------------------
# Public endpoints (no auth required)
# -------------------------


@router.get(
    "/",
    response_model=ProductList,
    status_code=status.HTTP_200_OK,
)
async def get_all_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category_id: int | None = Query(None, description="Filter by category ID"),
    search: str | None = Query(
        None, min_length=1, description="Search by product name"
    ),
    min_price: float | None = Query(None, ge=0, description="Minimum product price"),
    max_price: float | None = Query(None, ge=0, description="Maximum product price"),
    in_stock: bool | None = Query(
        None, description="true = in stock only, false = out of stock only"
    ),
    seller_id: int | None = Query(None, description="Filter by seller ID"),
    service: ProductService = Depends(get_product_service),
):
    """
    Retrieve all active products with pagination, filters and text search (public).

    Query parameters:
        - page        : page number, starts from 1 (default: 1)
        - page_size   : items per page, max 100 (default: 20)
        - category_id : filter by category
        - search      : case-insensitive substring search in product name
        - min_price   : minimum price (inclusive)
        - max_price   : maximum price (inclusive)
        - in_stock    : true = stock > 0, false = stock == 0
        - seller_id   : filter by seller
    """
    return await service.get_all_products(
        page=page,
        page_size=page_size,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        seller_id=seller_id,
        search=search,
    )


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


@router.get(
    "/{product_id}/reviews/",
    response_model=list[ReviewSchema],
    status_code=status.HTTP_200_OK,
)
async def get_product_reviews(
    product_id: int,
    service: ReviewService = Depends(get_review_service),
):
    """
    Retrieve all active reviews for a specific product (public).
    Returns 404 if the product does not exist or is inactive.
    """
    return await service.get_reviews_by_product(product_id)


# -------------------------
# Protected endpoints (seller only)
# -------------------------


@router.post(
    "/{product_id}/image",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def upload_product_image(
    product_id: int,
    file: UploadFile,
    service: ProductService = Depends(get_product_service),
    current_user: UserModel = Depends(get_current_seller),
):
    """
    Upload or replace the product image (seller only).
    Saves the new file first, then updates the DB.
    If the DB update fails, the newly saved file is cleaned up automatically.
    The old image file is deleted from disk after a successful DB update.
    """
    new_image_url = await save_product_image(file)
    try:
        product, old_image_url = await service.update_product_image(
            product_id, new_image_url, seller_id=current_user.id
        )
    except HTTPException:
        # DB update failed — remove the newly saved file to avoid orphaned files
        remove_product_image(new_image_url)
        raise
    # DB update succeeded — safe to delete the old image file
    remove_product_image(old_image_url)
    return product


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
    Removes the product image file from disk after successful DB soft delete.
    """
    product, old_image_url = await service.delete_product(product_id, seller_id=current_user.id)
    remove_product_image(old_image_url)
    return product
