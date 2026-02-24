from fastapi import HTTPException

from app.application.products.schemas import (
    Product as ProductSchema,
    ProductCreate,
)
from app.infrastructure.repositories.product import ProductRepository
from app.infrastructure.repositories.category import CategoryRepository


class ProductService:
    """
    Business logic layer for products.
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

    def _validate_category(self, category_id: int):
        """
        Validate that category exists and is active.
        """
        category = self.category_repository.get_active_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=400,
                detail="Category not found or inactive",
            )
        return category

    def _validate_product(self, product_id: int):
        """
        Validate that product exists and is active.
        """
        product = self.product_repository.get_active_by_id(product_id)
        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found or inactive",
            )
        return product

    # -------------------------
    # Public service methods
    # -------------------------

    def create_product(self, product_data: ProductCreate) -> ProductSchema:
        """
        Create a new product.

        - Validates that category exists and is active
        - Sets is_active=True by default
        """
        category_id = product_data.category_id

        # Validate category existence
        self._validate_category(category_id)

        # Prepare data for creation
        data = product_data.model_dump()
        data["is_active"] = True

        return self.product_repository.create(data)

    def get_all_products(self) -> list[ProductSchema]:
        """
        Retrieve all active products.
        """
        return self.product_repository.get_all_active()

    def get_products_by_category(self, category_id: int) -> list[ProductSchema]:
        """
        Retrieve active products by category.
        """

        # Validate category existence
        self._validate_category(category_id)

        return self.product_repository.get_active_by_category(category_id)

    def get_product(self, product_id: int) -> ProductSchema:
        """
        Retrieve single active product.

        - Validates product existence
        - Validates related category is still active
        """

        # Validate product existence
        product = self._validate_product(product_id)

        # Validate category existence
        self._validate_category(product.category_id)

        return product

    def update_product(
        self,
        product_id: int,
        product_data: ProductCreate,
    ) -> ProductSchema:
        """
        Update existing active product.
        """

        # Validate product existence
        product = self._validate_product(product_id)

        # Validate category existence
        self._validate_category(product_data.category_id)

        # Perform update
        return self.product_repository.update(
            product,
            product_data.model_dump(),
        )

    def delete_product(self, product_id: int) -> dict:
        """
        Logically delete product by setting is_active=False.
        """

        # Validate deletion result
        product = self.product_repository.soft_delete(product_id)
        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found or inactive",
            )

        return {
            "status": "success",
            "message": "Product marked as inactive",
        }
