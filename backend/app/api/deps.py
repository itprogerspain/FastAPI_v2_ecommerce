from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.db import get_db
from app.infrastructure.repositories.category import CategoryRepository
from app.application.categories.service import CategoryService
from app.infrastructure.repositories.product import ProductRepository
from app.application.products.service import ProductService


def get_category_service(
    db: Session = Depends(get_db),
) -> CategoryService:
    """
    Dependency that provides CategoryService instance.
    """
    repository = CategoryRepository(db)
    return CategoryService(repository)


def get_product_service(
    db: Session = Depends(get_db),
) -> ProductService:
    """
    Dependency that provides ProductService instance.
    """
    product_repository = ProductRepository(db)
    category_repository = CategoryRepository(db)

    return ProductService(
        product_repository,
        category_repository,
    )
