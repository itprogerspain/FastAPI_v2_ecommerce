from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db.order import Order as OrderModel, OrderItem as OrderItemModel


class OrderRepository:
    """
    Repository layer for order database operations (Asynchronous).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, order: OrderModel) -> OrderModel:
        """
        Persist a new order in the database.
        """
        self.db.add(order)
        await self.db.flush()
        return order

    async def add_order_item(self, order_item: OrderItemModel) -> None:
        """
        Persist a new order item.
        """
        self.db.add(order_item)

    async def get_order_with_items(self, order_id: int) -> OrderModel | None:
        """
        Load a single order with all its items and products eagerly loaded.

        Uses nested selectinload to avoid N+1 queries:
            1st query : fetch the order
            2nd query : fetch all OrderItems for that order (WHERE id IN (...))
            3rd query : fetch all Products for those OrderItems (WHERE id IN (...))

        This gives us the full Order -> OrderItem -> Product structure
        in memory with just 2–3 efficient queries.

        selectinload is preferred over joinedload here because:
            - No duplicate rows from JOINs on collections
            - Better performance on large result sets
        """
        result = await self.db.scalars(
            select(OrderModel)
            .options(
                selectinload(OrderModel.items).selectinload(OrderItemModel.product)
            )
            .where(OrderModel.id == order_id)
        )
        return result.first()

    async def count_user_orders(self, user_id: int) -> int:
        """
        Count total orders for pagination.
        """
        stmt = select(func.count(OrderModel.id)).where(OrderModel.user_id == user_id)
        return await self.db.scalar(stmt) or 0

    async def list_user_orders(
        self, user_id: int, page: int, page_size: int
    ) -> list[OrderModel]:
        """
        Retrieve paginated orders for a user.
        """
        stmt = (
            select(OrderModel)
            .options(
                selectinload(OrderModel.items).selectinload(OrderItemModel.product)
            )
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.scalars(stmt)
        return list(result.all())
