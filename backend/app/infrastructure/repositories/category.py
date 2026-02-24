from sqlalchemy import select
from sqlalchemy.orm import Session

# ORM model alias to avoid confusion with Pydantic CategorySchema
from app.models.db.category import Category as CategoryModel

# Common reusable conditions
ACTIVE_CATEGORY = CategoryModel.is_active.is_(True)


class CategoryRepository:
    """
    Repository layer for category database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        """
        Base query for active categories.
        """
        return select(CategoryModel).where(ACTIVE_CATEGORY)

    def get_active_by_id(self, category_id: int) -> CategoryModel | None:
        """
        Retrieve an active category by ID.
        """
        stmt = self._base_query().where(CategoryModel.id == category_id).limit(1)
        return self.db.scalars(stmt).first()

    def get_all_active(self) -> list[CategoryModel]:
        """
        Retrieve all active categories.
        """
        stmt = self._base_query().order_by(CategoryModel.id)
        return list(self.db.scalars(stmt))

    def create(self, data: dict) -> CategoryModel:
        """
        Create a new category in the database.
        """
        category = CategoryModel(**data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: CategoryModel, data: dict) -> CategoryModel:
        """
        Update an existing category with allowed fields only.
        """
        allowed_fields = {"name", "parent_id"}

        for field, value in data.items():
            if field in allowed_fields:
                setattr(category, field, value)

        self.db.commit()
        self.db.refresh(category)
        return category

    def soft_delete(self, category_id: int) -> CategoryModel | None:
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
