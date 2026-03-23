from decimal import Decimal

from fastapi import HTTPException, status

from app.application.products.schemas import (
    Product as ProductSchema,
    ProductCreate,
    ProductList,
)
from app.infrastructure.repositories.product import ProductRepository
from app.infrastructure.repositories.category import CategoryRepository


class ProductService:
    """
    Business logic layer for products (Asynchronous).
    Handles validation and delegates database operations to repositories.
    """

    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
    ):
        self.product_repository = product_repository
        self.category_repository = category_repository

    # -------------------------
    # Internal validation helpers
    # -------------------------

    async def _validate_category(self, category_id: int):
        """
        Validate that category exists and is active.
        """
        category = await self.category_repository.get_active_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found or inactive",
            )
        return category

    async def _validate_product(self, product_id: int):
        """
        Validate that product exists and is active.
        Uses simple query without category JOIN to avoid false 404 errors.
        """
        product = await self.product_repository.get_active_by_id_simple(product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or inactive",
            )
        return product

    @staticmethod
    def _validate_ownership(product, seller_id: int):
        """
        Validate that the product belongs to the given seller.
        Raises 403 Forbidden if seller_id does not match.
        """
        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify your own products",
            )

    # -------------------------
    # Public service methods
    # -------------------------

    async def get_all_products(
        self,
        page: int,
        page_size: int,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        in_stock: bool | None = None,
        seller_id: int | None = None,
    ) -> ProductList:
        """
        Retrieve active products with pagination and optional filters.

        Validates that min_price <= max_price before querying.
        Delegates filter logic to the repository layer.
        """
        # Validate price range logic
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_price cannot be greater than max_price",
            )

        items, total = await self.product_repository.get_all_active_paginated(
            page=page,
            page_size=page_size,
            category_id=category_id,
            min_price=Decimal(str(min_price)) if min_price is not None else None,
            max_price=Decimal(str(max_price)) if max_price is not None else None,
            in_stock=in_stock,
            seller_id=seller_id,
        )

        return ProductList(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_products_by_category(self, category_id: int) -> list[ProductSchema]:
        """
        Retrieve active products by category (public).
        """
        await self._validate_category(category_id)
        return await self.product_repository.get_active_by_category(category_id)

    async def get_product(self, product_id: int) -> ProductSchema:
        """
        Retrieve single active product (public).
        Uses JOIN-based query to ensure category is also active.
        """
        product = await self.product_repository.get_active_by_id(product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or inactive",
            )
        return product

    async def create_product(
        self,
        product_data: ProductCreate,
        seller_id: int,
    ) -> ProductSchema:
        """
        Create a new product bound to the given seller.
        """
        await self._validate_category(product_data.category_id)

        data = product_data.model_dump()
        data["is_active"] = True
        data["seller_id"] = seller_id

        return await self.product_repository.create(data)

    async def update_product(
        self,
        product_id: int,
        product_data: ProductCreate,
        seller_id: int,
    ) -> ProductSchema:
        """
        Update product. Only the owning seller can update it.
        """
        product = await self._validate_product(product_id)
        self._validate_ownership(product, seller_id)
        await self._validate_category(product_data.category_id)

        return await self.product_repository.update(product, product_data.model_dump())

    async def delete_product(
        self,
        product_id: int,
        seller_id: int,
    ) -> ProductSchema:
        """
        Logically delete product. Only the owning seller can delete it.
        """
        product = await self._validate_product(product_id)
        self._validate_ownership(product, seller_id)

        deleted = await self.product_repository.soft_delete(product_id)
        return deleted
