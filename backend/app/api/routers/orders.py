from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db.order import Order as OrderModel, OrderItem as OrderItemModel

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


async def _load_order_with_items(db: AsyncSession, order_id: int) -> OrderModel | None:
    """
    Load a single order with all its items and products eagerly loaded.

    Uses nested selectinload to avoid N+1 queries:
        1st query : fetch the order
        2nd query : fetch all OrderItems for that order (WHERE id IN (...))
        3rd query : fetch all Products for those OrderItems (WHERE id IN (...))

    This gives us the full Order -> OrderItem -> Product structure
    in memory with just 2-3 efficient queries.

    selectinload is preferred over joinedload here because:
        - No duplicate rows from JOINs on collections
        - Better performance on large result sets
    """
    result = await db.scalars(
        select(OrderModel)
        .options(
            selectinload(OrderModel.items).selectinload(OrderItemModel.product),
        )
        .where(OrderModel.id == order_id)
    )
    return result.first()
