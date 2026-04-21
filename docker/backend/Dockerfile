# ============================================================
# Stage 1 — Builder
# Install all Python dependencies with build tools available.
# This stage is thrown away after — only the installed packages
# are copied to the final image, keeping it clean and small.
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Disable .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build-time system dependencies.
# build-essential and libpq-dev are required to compile:
#   - asyncpg (PostgreSQL async driver)
#   - cryptography (used by PyJWT and passlib)
#   - bcrypt
# Cleaned up in the same layer to avoid bloating the image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies into an isolated prefix.
# Using --prefix=/install separates them from the system Python
# so we can copy only this folder into the runtime stage.
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt


# ============================================================
# Stage 2 — Runtime
# Minimal image — no compilers, no build tools.
# Only the app code and pre-built packages from stage 1.
# ============================================================
FROM python:3.12-slim AS runtime

WORKDIR /app/backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install only the runtime system libraries (not build tools).
# libpq5 is the PostgreSQL client library required by asyncpg at runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built Python packages from the builder stage
COPY --from=builder /install /usr/local

# Create a non-root user — running as root in a container is a security risk.
# UID/GID 1001 avoids conflicts with common system users.
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

# Copy application source code
COPY backend/ .

# Create runtime directories and hand ownership to the non-root user.
# logs/ and media/ are written at runtime so they must be writable.
RUN mkdir -p logs media/products \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Health check: hit the root endpoint every 30s.
# --start-period gives the app time to boot before checks begin.
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Gunicorn acts as the process manager, Uvicorn workers handle ASGI.
# This combination is more robust than uvicorn's built-in multi-process mode.
# Workers count follows the rule: 2 * CPU_cores + 1.
# Adjust --workers in docker-compose via the command override if needed.
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
