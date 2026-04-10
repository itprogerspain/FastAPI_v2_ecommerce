from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.api_v1 import api_v1_router

BASE_DIR = Path(__file__).resolve().parent.parent

# Create FastAPI application
app = FastAPI(
    title="FastAPI E-commerce API",
    version="0.1.0",
)

app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")

# Include all API v1 routes
app.include_router(api_v1_router)


# Root endpoint to check if API is running
@app.get("/")
async def root():
    """
    Root endpoint to confirm that the API is running.
    """
    return {"message": "Welcome to the e-commerce API!"}
