from fastapi import APIRouter, Depends, status

from app.application.reviews.schemas import Review as ReviewSchema, ReviewCreate
from app.application.reviews.service import ReviewService
from app.api.deps import get_review_service
from app.core.deps import get_current_user, get_current_buyer
from app.models.db.user import User as UserModel

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


# -------------------------
# Public endpoints (no auth required)
# -------------------------


@router.get(
    "/",
    response_model=list[ReviewSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_reviews(
    service: ReviewService = Depends(get_review_service),
):
    """
    Retrieve all active reviews (public).
    """
    return await service.get_all_reviews()


# -------------------------
# Protected endpoints
# -------------------------


@router.post(
    "/",
    response_model=ReviewSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    review_data: ReviewCreate,
    service: ReviewService = Depends(get_review_service),
    current_user: UserModel = Depends(get_current_buyer),
):
    """
    Create a new review for a product (buyers only).
    Automatically recalculates product rating after creation.
    """
    return await service.create_review(review_data, user_id=current_user.id)


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_review(
    review_id: int,
    service: ReviewService = Depends(get_review_service),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Soft delete a review by setting is_active=False.
    Allowed for: review author or admin.
    Automatically recalculates product rating after deletion.
    """
    return await service.delete_review(
        review_id,
        user_id=current_user.id,
        user_role=current_user.role,
    )


# TODO: Implement PUT /reviews/{review_id} endpoint for editing reviews
#  - Allow only the review author (buyer) to edit their own review
#  - Validate grade range (1-5)
#  - Recalculate product rating after update
#  - Add ReviewUpdate schema in schemas.py with optional comment and grade fields
#  - Add update() method to ReviewRepository
#  - Add update_review() method to ReviewService
