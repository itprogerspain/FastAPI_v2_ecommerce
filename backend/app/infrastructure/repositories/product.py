from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.product import Product as ProductModel
from app.models.db.category import Category as CategoryModel

# Common reusable conditions for cleaner queries
ACTIVE_PRODUCT = ProductModel.is_active.is_(True)
ACTIVE_CATEGORY = CategoryModel.is_active.is_(True)
IN_STOCK = ProductModel.stock > 0


class ProductRepository:
    """
    Repository layer for product database operations (Asynchronous).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _base_query():
        """
        Base query joining Product and Category with active filters.
        Used for public-facing queries that require an active category.
        """
        return (
            select(ProductModel)
            .join(CategoryModel)
            .where(ACTIVE_PRODUCT, ACTIVE_CATEGORY)
        )

    async def get_active_by_id(self, product_id: int) -> ProductModel | None:
        """
        Retrieve an active product by ID with an active category (via JOIN).
        Used for public GET endpoints where category must also be active.
        """
        stmt = self._base_query().where(ProductModel.id == product_id).limit(1)
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_active_by_id_simple(self, product_id: int) -> ProductModel | None:
        """
        Retrieve an active product by ID without category join.
        Used for ownership checks and write operations (PUT, DELETE)
        where we only need to confirm the product exists and is active.
        """
        stmt = (
            select(ProductModel)
            .where(ProductModel.id == product_id, ACTIVE_PRODUCT)
            .limit(1)
        )
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_all_active_paginated(
        self,
        page: int,
        page_size: int,
        category_id: int | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        in_stock: bool | None = None,
        seller_id: int | None = None,
    ) -> tuple[list[ProductModel], int]:
        """
        Retrieve active products with pagination and optional filters.

        Filters (all optional):
            - category_id : filter by category
            - min_price   : minimum price (inclusive)
            - max_price   : maximum price (inclusive)
            - in_stock    : True = stock > 0, False = stock == 0
            - seller_id   : filter by seller

        Returns a tuple of:
            - items : list of ProductModel for the current page
            - total : total count matching the filters (for pagination metadata)
        """
        # Build dynamic filter list — all conditions combined with AND
        filters = [ACTIVE_PRODUCT]

        if category_id is not None:
            filters.append(ProductModel.category_id == category_id)
        if min_price is not None:
            filters.append(ProductModel.price >= min_price)
        if max_price is not None:
            filters.append(ProductModel.price <= max_price)
        if in_stock is not None:
            filters.append(
                ProductModel.stock > 0 if in_stock else ProductModel.stock == 0
            )
        if seller_id is not None:
            filters.append(ProductModel.seller_id == seller_id)

        # Count total matching products (same filters, no pagination)
        total_stmt = select(func.count()).select_from(ProductModel).where(*filters)
        total = await self.db.scalar(total_stmt) or 0

        # Fetch paginated products with the same filters
        products_stmt = (
            select(ProductModel)
            .where(*filters)
            .order_by(ProductModel.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.scalars(products_stmt)
        items = list(result.all())

        return items, total

    async def get_active_by_category(self, category_id: int) -> list[ProductModel]:
        """
        Retrieve active products by category ID with active category and stock > 0.
        """
        stmt = (
            self._base_query()
            .where(
                ProductModel.category_id == category_id,
                IN_STOCK,
            )
            .order_by(ProductModel.id)
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def create(self, data: dict) -> ProductModel:
        """
        Create a new product in the database.
        """
        product = ProductModel(**data)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, product: ProductModel, data: dict) -> ProductModel:
        """
        Update existing product fields safely.
        """
        allowed_fields = {
            "name",
            "description",
            "price",
            "image_url",
            "stock",
            "category_id",
        }

        for field, value in data.items():
            if field in allowed_fields:
                setattr(product, field, value)

        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def soft_delete(self, product_id: int) -> ProductModel | None:
        """
        Logically delete product by setting is_active=False.
        Uses get_active_by_id_simple to avoid JOIN issues.
        """
        product = await self.get_active_by_id_simple(product_id)
        if product is None:
            return None

        product.is_active = False
        await self.db.commit()
        await self.db.refresh(product)
        return product
