from celery import Celery
from celery.schedules import crontab

from app.core.config import REDIS_URL

# Create the Celery application instance.
# The first argument is the name of the current module — used by Celery
# to generate task names automatically (e.g. "app.tasks.email.send_order_confirmation").
celery_app = Celery("app")

celery_app.conf.update(
    # -----------------------------------------------------------------
    # Broker and result backend — both use Redis.
    # Broker   : receives tasks from FastAPI and delivers to workers.
    # Backend  : stores task results (status, return value, errors).
    # -----------------------------------------------------------------
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,

    # -----------------------------------------------------------------
    # Serialization — JSON is safe and human-readable.
    # Never use "pickle" in production (security risk).
    # -----------------------------------------------------------------
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # -----------------------------------------------------------------
    # Timezone settings.
    # -----------------------------------------------------------------
    timezone="Europe/Moscow",
    enable_utc=True,

    # -----------------------------------------------------------------
    # Task discovery — Celery will import these modules on startup
    # and register all @celery_app.task functions found inside.
    # Add new task modules here as the project grows.
    # -----------------------------------------------------------------
    include=[
        "app.tasks.email",
        "app.tasks.orders",
        "app.tasks.products",
    ],

    # -----------------------------------------------------------------
    # Reliability settings.
    # -----------------------------------------------------------------
    # Track when a worker picks up a task (useful for monitoring).
    task_track_started=True,

    # Retry broker connection on startup instead of crashing immediately.
    # Important in Docker — Redis container may start slightly after the worker.
    broker_connection_retry_on_startup=True,

    # -----------------------------------------------------------------
    # Celery Beat — periodic task schedule.
    # Beat is a separate process that acts as a scheduler:
    # it sends tasks to the broker at the configured times,
    # and workers pick them up as usual.
    # Run beat with: celery -A app.core.celery.celery_app beat --loglevel=info
    # -----------------------------------------------------------------
    beat_schedule={
        "send-abandoned-cart-reminder-daily": {
            "task": "tasks.send_abandoned_cart_reminder",
            # Every day at 10:00 AM (server timezone — Europe/Moscow set above)
            "schedule": crontab(hour=10, minute=0),
        },
    },
)
