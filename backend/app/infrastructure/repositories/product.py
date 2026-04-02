from decimal import Decimal

from sqlalchemy import select, func, desc
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
        search: str | None = None,
    ) -> tuple[list[ProductModel], int]:
        """
        Retrieve active products with pagination, optional filters and full-text search.

        When search is provided:
            - Uses PostgreSQL FTS with websearch_to_tsquery (web-like syntax)
            - Matches against tsv computed column (name weight A, description weight B)
            - Results are ranked by ts_rank_cd (coverage density algorithm)
            - Sorting: relevance DESC, then id ASC

        When search is not provided:
            - Simple filters with ORDER BY id

        Filters (all optional):
            - category_id : filter by category
            - min_price   : minimum price (inclusive)
            - max_price   : maximum price (inclusive)
            - in_stock    : True = stock > 0, False = stock == 0
            - seller_id   : filter by seller
            - search      : full-text search query (web syntax supported)

        Returns a tuple of:
            - items : list of ProductModel for the current page
            - total : total count matching all filters
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

        # Full-text search via PostgreSQL FTS
        rank_col = None
        if search:
            search_value = search.strip()
            if search_value:
                # websearch_to_tsquery supports web-like syntax: quotes, minus, AND/OR
                ts_query = func.websearch_to_tsquery("english", search_value)

                # @@ operator checks if tsv matches the ts_query
                filters.append(ProductModel.tsv.op("@@")(ts_query))

                # ts_rank_cd: coverage density ranking — stable with long texts
                # Words with weight 'A' (name) score higher than 'B' (description)
                rank_col = func.ts_rank_cd(ProductModel.tsv, ts_query).label("rank")

        # Count total matching products (same filters, no pagination)
        total_stmt = select(func.count()).select_from(ProductModel).where(*filters)
        total = await self.db.scalar(total_stmt) or 0

        # Fetch paginated products
        if rank_col is not None:
            # When searching: sort by relevance DESC, then id ASC for stable order
            products_stmt = (
                select(ProductModel, rank_col)
                .where(*filters)
                .order_by(desc(rank_col), ProductModel.id)
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            result = await self.db.execute(products_stmt)
            items = [row[0] for row in result.all()]
        else:
            # Without search: simple sort by id
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
