from fastapi import HTTPException

from app.application.categories.schemas import (
    Category as CategorySchema,
    CategoryCreate,
    CategoryUpdate,
)
from app.infrastructure.repositories.category import CategoryRepository


class CategoryService:
    """
    Business logic layer for categories (Asynchronous).
    Handles validation and delegates database operations to CategoryRepository.
    """

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    # -------------------------
    # Internal validation helpers (Now async)
    # -------------------------

    async def _validate_category(self, category_id: int):
        """
        Validate that category exists and is active.
        """
        # Added await
        category = await self.repository.get_active_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )
        return category

    async def _validate_parent(self, parent_id: int, category_id: int | None = None):
        """
        Validate parent category rules:
        - Parent must exist
        - Cannot be the same as the category itself
        - Cannot create a direct cycle
        """
        # Prevent category from being its own parent
        if category_id is not None and parent_id == category_id:
            raise HTTPException(
                status_code=400,
                detail="Category cannot be its own parent",
            )

        # Added await
        parent = await self.repository.get_active_by_id(parent_id)
        if parent is None:
            raise HTTPException(
                status_code=400,
                detail="Parent category not found",
            )

        # Prevent direct cyclic relationship
        if (
            category_id is not None
            and getattr(parent, "parent_id", None) == category_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Cyclical relationship detected",
            )

        return parent

    # -------------------------
    # Public service methods (Now async)
    # -------------------------

    async def create_category(self, category_data: CategoryCreate) -> CategorySchema:
        """
        Create a new category with validation.
        """
        parent_id = category_data.parent_id

        # Validate parent category if provided
        if parent_id is not None:
            await self._validate_parent(parent_id)

        # Added await
        return await self.repository.create(category_data.model_dump())

    async def get_all_categories(self) -> list[CategorySchema]:
        """
        Retrieve all active categories.
        """
        # Added await
        return await self.repository.get_all_active()

    async def delete_category(self, category_id: int) -> dict:
        """
        Logically delete a category by setting is_active=False.
        """
        # Added await
        category = await self.repository.soft_delete(category_id)

        # Validate deletion result
        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        return {
            "status": "success",
            "message": "Category marked as inactive",
        }

    async def update_category(
        self, category_id: int, data: CategoryUpdate
    ) -> CategorySchema:
        """
        Update an active category by its ID.
        """

        # Added await for validation
        category = await self._validate_category(category_id)

        parent_id = data.parent_id

        # Validate parent category if provided
        if parent_id is not None:
            await self._validate_parent(parent_id, category.id)

        # Added await
        return await self.repository.update(category, data.model_dump())
