from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # Changed to AsyncSession

# ORM model alias to avoid confusion with Pydantic CategorySchema
from app.models.db.category import Category as CategoryModel

# Common reusable conditions
ACTIVE_CATEGORY = CategoryModel.is_active.is_(True)


class CategoryRepository:
    """
    Repository layer for category database operations (Asynchronous).
    """

    def __init__(self, db: AsyncSession):  # Type hint changed to AsyncSession
        self.db = db

    @staticmethod
    def _base_query():
        """
        Base query for active categories.
        """
        return select(CategoryModel).where(ACTIVE_CATEGORY)

    async def get_active_by_id(self, category_id: int) -> CategoryModel | None:
        """
        Retrieve an active category by ID.
        """
        stmt = self._base_query().where(CategoryModel.id == category_id).limit(1)
        # First await scalars, then get first element
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_all_active(self) -> list[CategoryModel]:
        """
        Retrieve all active categories.
        """
        stmt = self._base_query().order_by(CategoryModel.id)
        # First await scalars, then convert to list
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def create(self, data: dict) -> CategoryModel:
        """
        Create a new category in the database.
        """
        category = CategoryModel(**data)
        self.db.add(category)
        await self.db.commit()  # Added await
        await self.db.refresh(category)  # Added await
        return category

    async def update(self, category: CategoryModel, data: dict) -> CategoryModel:
        """
        Update an existing category with allowed fields only.
        """
        allowed_fields = {"name", "parent_id"}

        for field, value in data.items():
            if field in allowed_fields:
                setattr(category, field, value)

        await self.db.commit()  # Added await
        await self.db.refresh(category)  # Added await
        return category

    async def soft_delete(self, category_id: int) -> CategoryModel | None:
        """
        Logically delete a category by setting is_active=False.
        """
        # Await internal async call
        category = await self.get_active_by_id(category_id)
        if category is None:
            return None

        category.is_active = False
        await self.db.commit()  # Added await
        await self.db.refresh(category)  # Added await
        return category
