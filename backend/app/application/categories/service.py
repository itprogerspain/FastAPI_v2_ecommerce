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

    def get_all_categories(self):
        """
        Retrieve all active categories.
        """
        return self.repository.get_all_active()

    def delete_category(self, category_id: int):
        """
        Logically delete a category.
        """
        category = self.repository.soft_delete(category_id)

        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        return {"status": "success", "message": "Category marked as inactive"}
