import asyncio
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from app.core.celery import celery_app
from app.core.config import (
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM,
    MAIL_FROM_NAME,
    MAIL_PORT,
    MAIL_SERVER,
)

# Path to the email templates directory
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "email"

# SMTP connection configuration for fastapi-mail.
# STARTTLS (port 587) is used — standard for Gmail and most providers.
# For SSL (port 465) set MAIL_SSL_TLS=True and MAIL_STARTTLS=False instead.
_mail_config = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    TEMPLATE_FOLDER=_TEMPLATES_DIR,
)


@celery_app.task(name="tasks.send_order_confirmation")
def send_order_confirmation(
    user_email: str,
    user_name: str,
    order_id: int,
    total_amount: str,
) -> None:
    """
    Background task: sends an order confirmation email to the buyer.
    Called immediately after a new order is created.

    Parameters are plain types (str, int) — Celery serializes via JSON,
    so avoid passing complex objects like Pydantic models or ORM instances.
    """
    asyncio.run(_send_order_confirmation(user_email, user_name, order_id, total_amount))


@celery_app.task(name="tasks.send_order_status_update")
def send_order_status_update(
    user_email: str,
    user_name: str,
    order_id: int,
    new_status: str,
) -> None:
    """
    Background task: notifies the buyer when their order status changes.
    Called each time order status is updated (paid, shipped, delivered).
    """
    asyncio.run(_send_order_status_update(user_email, user_name, order_id, new_status))


@celery_app.task(name="tasks.send_password_reset")
def send_password_reset(
    user_email: str,
    user_name: str,
    reset_link: str,
) -> None:
    """
    Background task: sends a password reset email with a secure link.
    Called when a user requests a password reset.
    """
    asyncio.run(_send_password_reset(user_email, user_name, reset_link))


# -------------------------
# Async implementations
# -------------------------
# Celery tasks are synchronous — async logic is wrapped in asyncio.run().
# Each function creates its own FastMail instance (stateless, safe for concurrent workers).

async def _send_order_confirmation(
    user_email: str,
    user_name: str,
    order_id: int,
    total_amount: str,
) -> None:
    message = MessageSchema(
        subject=f"Order #{order_id} Confirmed",
        recipients=[user_email],
        template_body={
            "user_name": user_name,
            "order_id": order_id,
            "total_amount": total_amount,
        },
        subtype=MessageType.html,
    )
    await FastMail(_mail_config).send_message(message, template_name="order_confirmation.html")


async def _send_order_status_update(
    user_email: str,
    user_name: str,
    order_id: int,
    new_status: str,
) -> None:
    message = MessageSchema(
        subject=f"Order #{order_id} Status Update",
        recipients=[user_email],
        template_body={
            "user_name": user_name,
            "order_id": order_id,
            "new_status": new_status,
        },
        subtype=MessageType.html,
    )
    await FastMail(_mail_config).send_message(message, template_name="order_status_update.html")


async def _send_password_reset(
    user_email: str,
    user_name: str,
    reset_link: str,
) -> None:
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[user_email],
        template_body={
            "user_name": user_name,
            "reset_link": reset_link,
        },
        subtype=MessageType.html,
    )
    await FastMail(_mail_config).send_message(message, template_name="password_reset.html")


@celery_app.task(name="tasks.send_cart_reminder")
def send_cart_reminder(user_email: str, shop_url: str) -> None:
    """
    Background task: sends an abandoned cart reminder email.
    Called by the periodic send_abandoned_cart_reminder task in orders.py.
    """
    asyncio.run(_send_cart_reminder(user_email, shop_url))


async def _send_cart_reminder(user_email: str, shop_url: str) -> None:
    message = MessageSchema(
        subject="You left something in your cart!",
        recipients=[user_email],
        template_body={"shop_url": shop_url},
        subtype=MessageType.html,
    )
    await FastMail(_mail_config).send_message(message, template_name="abandoned_cart.html")
