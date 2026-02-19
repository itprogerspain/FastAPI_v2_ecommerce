from fastapi import HTTPException

from app.application.categories.schemas import (
    Category as CategorySchema,
    CategoryCreate,
    CategoryUpdate,
)
from app.infrastructure.repositories.category import CategoryRepository


class CategoryService:
    """
    Business logic layer for categories.
    Handles validation and delegates database operations to CategoryRepository.
    """

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def create_category(self, category_data: CategoryCreate) -> CategorySchema:
        """
        Create a new category with validation.

        - Validates that the parent category exists if parent_id is provided.
        - Returns the created category as Pydantic schema.
        """
        if category_data.parent_id is not None:
            parent = self.repository.get_active_by_id(category_data.parent_id)
            if parent is None:
                raise HTTPException(
                    status_code=400,
                    detail="Parent category not found",
                )

        category = self.repository.create(category_data.model_dump())
        return category  # FastAPI will convert CategoryModel to Pydantic CategorySchema

    def get_all_categories(self) -> list[CategorySchema]:
        """
        Retrieve all active categories.

        Returns a list of active CategorySchema instances.
        """
        return self.repository.get_all_active()

    def delete_category(self, category_id: int) -> dict:
        """
        Logically delete a category by setting is_active=False.

        Raises 404 if the category does not exist or is already inactive.
        """
        category = self.repository.soft_delete(category_id)
        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )
        return {"status": "success", "message": "Category marked as inactive"}

    def update_category(self, category_id: int, data: CategoryUpdate) -> CategorySchema:
        """
        Update an active category by its ID.

        - Validates category existence
        - Validates parent category if provided
        - Prevents self-parenting and direct cycles
        - Updates allowed fields (name, parent_id)
        """

        # Validate category existence
        category = self.repository.get_active_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        # Validate parent category if provided
        if data.parent_id is not None:
            # Prevent category from being its own parent
            if data.parent_id == category.id:
                raise HTTPException(
                    status_code=400,
                    detail="Category cannot be its own parent",
                )

            parent = self.repository.get_active_by_id(data.parent_id)
            if parent is None:
                raise HTTPException(
                    status_code=400,
                    detail="Parent category not found",
                )

            # Prevent direct cyclic relationship: parent.parent == category
            if getattr(parent, "parent_id", None) == category.id:
                raise HTTPException(
                    status_code=400,
                    detail="Cyclical relationship detected",
                )

        # Perform update
        return self.repository.update(category, data.model_dump())
