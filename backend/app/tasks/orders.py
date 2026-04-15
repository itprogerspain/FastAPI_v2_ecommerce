import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.celery import celery_app
from app.infrastructure.db import async_session_maker
from app.models.db.order import Order as OrderModel
from app.models.db.cart import CartItem as CartItemModel
from app.models.db.user import User as UserModel

# URL of the shop frontend — used in abandoned cart reminder emails.
# TODO: move to config.py / .env when frontend URL is finalized
SHOP_URL = "http://localhost:3000/cart"


@celery_app.task(name="tasks.auto_cancel_unpaid_order")
def auto_cancel_unpaid_order(order_id: int) -> None:
    """
    Countdown task: automatically cancels an order if it is still 'pending'
    after 30 minutes (the allowed payment window).

    This is NOT a periodic task — it is triggered once per order at creation:
        auto_cancel_unpaid_order.apply_async(args=[order.id], countdown=1800)

    If the order was already paid or cancelled before the timer fires,
    the task exits silently without any changes.

    TODO: add the .apply_async() call to the orders service when a new order is created.
    """
    asyncio.run(_auto_cancel_unpaid_order(order_id))


@celery_app.task(name="tasks.send_abandoned_cart_reminder")
def send_abandoned_cart_reminder() -> None:
    """
    Periodic task (Celery Beat): finds users who have not updated their cart
    for more than 24 hours and sends each of them a reminder email.

    Runs every day at 10:00 AM — configured in celery.py beat_schedule.
    One email per user regardless of the number of items in their cart.
    """
    asyncio.run(_send_abandoned_cart_reminder())


# -------------------------
# Async implementations
# -------------------------

async def _auto_cancel_unpaid_order(order_id: int) -> None:
    async with async_session_maker() as session:
        # Load order with user eagerly to access user.email for the notification
        result = await session.scalars(
            select(OrderModel)
            .options(selectinload(OrderModel.user))
            .where(OrderModel.id == order_id)
        )
        order = result.first()

        # Order not found or already paid / cancelled — nothing to do
        if not order or order.status != "pending":
            return

        order.status = "cancelled"
        await session.commit()

        # Notify user about auto-cancellation
        # Import inside function to avoid circular imports at module load time
        from app.tasks.email import send_order_status_update
        send_order_status_update.delay(
            user_email=order.user.email,
            user_name=order.user.email,
            order_id=order.id,
            new_status="cancelled (payment timeout)",
        )


async def _send_abandoned_cart_reminder() -> None:
    threshold = datetime.now(timezone.utc) - timedelta(hours=24)

    async with async_session_maker() as session:
        # Find distinct users who have cart items not updated for 24+ hours
        result = await session.scalars(
            select(UserModel)
            .join(CartItemModel, CartItemModel.user_id == UserModel.id)
            .where(CartItemModel.updated_at < threshold)
            .distinct()
        )
        users = list(result.all())

        # Send one reminder email per user
        from app.tasks.email import send_cart_reminder
        for user in users:
            send_cart_reminder.delay(
                user_email=user.email,
                shop_url=SHOP_URL,
            )
