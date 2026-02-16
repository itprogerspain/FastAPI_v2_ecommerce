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
