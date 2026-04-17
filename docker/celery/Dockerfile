# Celery worker and beat scheduler image.
# Identical build process to the backend — same dependencies, same app code.
# The only difference is the CMD (overridden per service in docker-compose):
#   worker : celery -A app.core.celery.celery_app worker --loglevel=info
#   beat   : celery -A app.core.celery.celery_app beat   --loglevel=info
#   flower : celery -A app.core.celery.celery_app flower
#
# We keep a separate Dockerfile (instead of reusing backend's) so that
# Celery containers can be tuned independently in the future
# (e.g. different base image, extra system libs for task-specific tools).

# ============================================================
# Stage 1 — Builder
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt


# ============================================================
# Stage 2 — Runtime
# ============================================================
FROM python:3.12-slim AS runtime

WORKDIR /app/backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

COPY backend/ .

RUN mkdir -p logs media/products \
    && chown -R appuser:appgroup /app

USER appuser

# Default command runs the Celery worker.
# Override in docker-compose for beat and flower services.
CMD ["celery", "-A", "app.core.celery.celery_app", "worker", "--loglevel=info"]
