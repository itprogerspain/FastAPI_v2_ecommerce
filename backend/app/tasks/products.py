import asyncio

from sqlalchemy import select
from sqlalchemy.sql import func

from app.core.celery import celery_app
from app.infrastructure.db import async_session_maker
from app.models.db.product import Product as ProductModel
from app.models.db.review import Review as ReviewModel


@celery_app.task(name="tasks.recalculate_product_rating")
def recalculate_product_rating(product_id: int) -> None:
    """
    Background task: recalculates the average product rating
    based on all active reviews and updates the product record.

    Called after a review is created or deleted — replaces the
    synchronous update that previously blocked the API response.

    Celery tasks are synchronous by default, so we use asyncio.run()
    to execute the async DB logic inside the sync task function.
    """
    asyncio.run(_recalculate(product_id))


async def _recalculate(product_id: int) -> None:
    """
    Async implementation of the rating recalculation.

    Opens its own DB session independently of FastAPI's DI system —
    Celery workers have no access to request-scoped dependencies.
    """
    async with async_session_maker() as session:
        # Calculate average grade from all active reviews for this product
        stmt = select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active.is_(True),
        )
        result = await session.execute(stmt)
        avg_rating = result.scalar() or 0.0

        # Update the product rating field
        product = await session.get(ProductModel, product_id)
        if product:
            product.rating = round(float(avg_rating), 2)
            await session.commit()
