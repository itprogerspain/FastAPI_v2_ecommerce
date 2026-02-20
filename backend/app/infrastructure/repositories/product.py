from sqlalchemy import select, update
from sqlalchemy.orm import Session

# ORM model alias to avoid confusion with Pydantic Product schema
from app.models.db.product import Product as ProductModel
from app.models.db.category import Category as CategoryModel


class ProductRepository:
    """
    Repository layer for product database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_active_by_id(self, product_id: int) -> ProductModel | None:
        """
        Retrieve an active product by ID.
        """
        stmt = select(ProductModel).where(
            ProductModel.id == product_id,
            ProductModel.is_active.is_(True),
        )
        return self.db.scalars(stmt).first()

    def get_all_active(self) -> list[ProductModel]:
        """
        Retrieve all active products.
        """
        stmt = select(ProductModel).where(ProductModel.is_active.is_(True))
        return list(self.db.scalars(stmt))

    def get_active_by_category(self, category_id: int) -> list[ProductModel]:
        """
        Retrieve active products by category ID.
        """
        stmt = select(ProductModel).where(
            ProductModel.category_id == category_id,
            ProductModel.is_active.is_(True),
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
        Update existing product fields.
        """
        for field, value in data.items():
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
