from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db.product import Product as ProductModel
from app.models.db.category import Category as CategoryModel

# Common reusable conditions for cleaner queries
ACTIVE_PRODUCT = ProductModel.is_active.is_(True)
ACTIVE_CATEGORY = CategoryModel.is_active.is_(True)
IN_STOCK = ProductModel.stock > 0


class ProductRepository:
    """
    Repository layer for product database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        """
        Base query joining Product and Category with active filters.
        """
        return (
            select(ProductModel)
            .join(CategoryModel)
            .where(ACTIVE_PRODUCT, ACTIVE_CATEGORY)
        )

    def get_active_by_id(self, product_id: int) -> ProductModel | None:
        """
        Retrieve an active product by ID with an active category.
        """
        stmt = self._base_query().where(ProductModel.id == product_id).limit(1)
        return self.db.scalars(stmt).first()

    def get_all_active(self) -> list[ProductModel]:
        """
        Retrieve all active products with active categories and stock > 0.
        """
        stmt = self._base_query().where(IN_STOCK).order_by(ProductModel.id)
        return list(self.db.scalars(stmt))

    def get_active_by_category(self, category_id: int) -> list[ProductModel]:
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
        return list(self.db.scalars(stmt))

    def create(self, data: dict) -> ProductModel:
        """
        Create a new product in the database.
        """
        product = ProductModel(**data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: ProductModel, data: dict) -> ProductModel:
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

        self.db.commit()
        self.db.refresh(product)
        return product

    def soft_delete(self, product_id: int) -> ProductModel | None:
        """
        Logically delete product by setting is_active=False.
        """
        product = self.get_active_by_id(product_id)
        if product is None:
            return None

        product.is_active = False
        self.db.commit()
        self.db.refresh(product)
        return product
