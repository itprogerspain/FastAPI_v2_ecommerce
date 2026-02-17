from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db.category import Category


class CategoryRepository:
    """
    Repository layer for category database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_active_by_id(self, category_id: int) -> Category | None:
        """
        Retrieve an active category by ID.
        """
        stmt = select(Category).where(
            Category.id == category_id,
            Category.is_active == True,
        )
        return self.db.scalars(stmt).first()

    def create(self, data: dict) -> Category:
        """
        Create a new category in the database.
        """
        category = Category(**data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_all_active(self) -> list[Category]:
        """
        Retrieve all active categories.
        """
        stmt = select(Category).where(Category.is_active.is_(True))
        return list(self.db.scalars(stmt))

    def soft_delete(self, category_id: int) -> Category | None:
        """
        Logically delete a category by setting is_active=False.
        """
        category = self.get_active_by_id(category_id)

        if category is None:
            return None

        category.is_active = False
        self.db.commit()
        self.db.refresh(category)

        return category
