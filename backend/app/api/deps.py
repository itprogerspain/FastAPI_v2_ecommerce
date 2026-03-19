from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db import get_async_db
from app.infrastructure.repositories.category import CategoryRepository
from app.application.categories.service import CategoryService
from app.infrastructure.repositories.product import ProductRepository
from app.application.products.service import ProductService
from app.infrastructure.repositories.user import UserRepository
from app.application.users.service import UserService


async def get_category_service(
    db: AsyncSession = Depends(get_async_db),
) -> CategoryService:
    """
    Dependency that provides CategoryService instance using an async session.
    """
    repository = CategoryRepository(db)
    return CategoryService(repository)


async def get_product_service(
    db: AsyncSession = Depends(get_async_db),
) -> ProductService:
    """
    Dependency that provides ProductService instance using an async session.
    """
    product_repository = ProductRepository(db)
    category_repository = CategoryRepository(db)

    return ProductService(
        product_repository,
        category_repository,
    )


async def get_user_service(
    db: AsyncSession = Depends(get_async_db),
) -> UserService:
    """
    Dependency that provides UserService instance using an async session.
    """
    repository = UserRepository(db)
    return UserService(repository)
