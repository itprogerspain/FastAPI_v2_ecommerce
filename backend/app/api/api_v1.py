from fastapi import APIRouter
from .routers import auth, categories, products, users, orders, cart, profiles, reviews, pages

# Main router for API version 1
api_v1_router = APIRouter(prefix="/api/v1")  # versioning prefix

# Include all routers
api_v1_router.include_router(categories.router)
api_v1_router.include_router(products.router)
# api_v1_router.include_router(users.router)
# api_v1_router.include_router(orders.router)
# api_v1_router.include_router(cart.router)
# api_v1_router.include_router(profiles.router)
# api_v1_router.include_router(reviews.router)
# api_v1_router.include_router(pages.router)
# api_v1_router.include_router(auth.router)