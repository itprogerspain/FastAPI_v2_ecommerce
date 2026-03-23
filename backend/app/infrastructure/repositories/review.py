from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.review import Review as ReviewModel
from app.models.db.product import Product as ProductModel


class ReviewRepository:
    """
    Repository layer for review database operations (Asynchronous).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_active(self) -> list[ReviewModel]:
        """
        Retrieve all active reviews.
        """
        stmt = select(ReviewModel).where(ReviewModel.is_active.is_(True))
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_active_by_product(self, product_id: int) -> list[ReviewModel]:
        """
        Retrieve all active reviews for a specific product.
        """
        stmt = select(ReviewModel).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active.is_(True),
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_active_by_id(self, review_id: int) -> ReviewModel | None:
        """
        Retrieve a single active review by ID.
        """
        stmt = (
            select(ReviewModel)
            .where(ReviewModel.id == review_id, ReviewModel.is_active.is_(True))
            .limit(1)
        )
        result = await self.db.scalars(stmt)
        return result.first()

    async def create(self, data: dict) -> ReviewModel:
        """
        Create a new review in the database.
        """
        review = ReviewModel(**data)
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def soft_delete(self, review: ReviewModel) -> ReviewModel:
        """
        Logically delete a review by setting is_active=False.
        """
        review.is_active = False
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def update_product_rating(self, product_id: int) -> None:
        """
        Recalculate and update the average rating for a product
        based on all active reviews.
        Sets rating to 0.0 if no active reviews remain.
        """
        stmt = select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active.is_(True),
        )
        result = await self.db.execute(stmt)
        avg_rating = result.scalar() or 0.0

        product = await self.db.get(ProductModel, product_id)
        if product:
            product.rating = avg_rating
            await self.db.commit()

    # TODO: Implement update() method
    #  - Accept review object and data dict with allowed fields: comment, grade
    #  - Use setattr pattern (like in product/category repositories)
