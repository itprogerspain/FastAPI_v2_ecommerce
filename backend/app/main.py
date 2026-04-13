from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.api_v1 import api_v1_router
from app.core.config import SECRET_KEY
from app.core.middleware import log_middleware

BASE_DIR = Path(__file__).resolve().parent.parent

# Create FastAPI application
app = FastAPI(
    title="FastAPI E-commerce API",
    version="0.1.0",
)

app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")

app.middleware("http")(log_middleware)

# Session middleware — required for:
# - anonymous user cart (stored in session cookie)
# - OAuth2 / social login (temporary state between redirects)
# Not actively used yet — will be wired up when those features are implemented.
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=1209600,  # 2 weeks in seconds (default)
    same_site="lax",
    https_only=False,  # TODO: set to True in production (requires HTTPS)
)

# Include all API v1 routes
app.include_router(api_v1_router)


# Root endpoint to check if API is running
@app.get("/")
async def root():
    """
    Root endpoint to confirm that the API is running.
    """
    return {"message": "Welcome to the e-commerce API!"}
