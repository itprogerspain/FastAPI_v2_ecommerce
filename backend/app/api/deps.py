from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.db import get_db
from app.infrastructure.repositories.category import CategoryRepository
from app.application.categories.service import CategoryService


def get_category_service(
    db: Session = Depends(get_db),
) -> CategoryService:
    """
    Dependency that provides CategoryService instance.
    """
    repository = CategoryRepository(db)
    return CategoryService(repository)
