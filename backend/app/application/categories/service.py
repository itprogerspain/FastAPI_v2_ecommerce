from fastapi import HTTPException

from app.application.categories.schemas import CategoryCreate
from app.infrastructure.repositories.category import CategoryRepository


class CategoryService:
    """
    Business logic layer for categories.
    """

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def create_category(self, category_data: CategoryCreate):
        """
        Create a new category with validation.
        """

        # Validate parent category if provided
        if category_data.parent_id is not None:
            parent = self.repository.get_active_by_id(category_data.parent_id)

            if parent is None:
                raise HTTPException(
                    status_code=400,
                    detail="Parent category not found",
                )

        return self.repository.create(category_data.model_dump())
