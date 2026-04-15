from fastapi import HTTPException, status

from app.application.reviews.schemas import ReviewCreate, Review as ReviewSchema
from app.infrastructure.repositories.review import ReviewRepository
from app.infrastructure.repositories.product import ProductRepository
from app.tasks.products import recalculate_product_rating


class ReviewService:
    """
    Business logic layer for reviews (Asynchronous).
    Handles validation and delegates database operations to ReviewRepository.
    """

    def __init__(
        self,
        review_repository: ReviewRepository,
        product_repository: ProductRepository,
    ):
        self.review_repository = review_repository
        self.product_repository = product_repository

    async def _validate_product(self, product_id: int):
        """
        Validate that the product exists and is active.
        """
        product = await self.product_repository.get_active_by_id_simple(product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or inactive",
            )
        return product

    async def get_all_reviews(self) -> list[ReviewSchema]:
        """
        Retrieve all active reviews (public).
        """
        return await self.review_repository.get_all_active()

    async def get_reviews_by_product(self, product_id: int) -> list[ReviewSchema]:
        """
        Retrieve all active reviews for a specific product (public).
        """
        await self._validate_product(product_id)
        return await self.review_repository.get_active_by_product(product_id)

    async def create_review(
        self,
        review_data: ReviewCreate,
        user_id: int,
    ) -> ReviewSchema:
        """
        Create a new review for a product (buyers only).
        Recalculates product rating after creation.
        """
        await self._validate_product(review_data.product_id)

        data = {
            "user_id": user_id,
            "product_id": review_data.product_id,
            "comment": review_data.comment,
            "grade": review_data.grade,
            "is_active": True,
        }

        review = await self.review_repository.create(data)

        # Recalculate product rating asynchronously after new review is added.
        # .delay() sends the task to Redis — worker picks it up in the background.
        # The API response is returned immediately without waiting for recalculation.
        recalculate_product_rating.delay(review_data.product_id)

        return review

    async def delete_review(
        self,
        review_id: int,
        user_id: int,
        user_role: str,
    ) -> dict:
        """
        Soft delete a review (author or admin only).
        Recalculates product rating after deletion.
        """
        review = await self.review_repository.get_active_by_id(review_id)
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found or already deleted",
            )

        # Only the review author or admin can delete
        if review.user_id != user_id and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews",
            )

        product_id = review.product_id
        await self.review_repository.soft_delete(review)

        # Recalculate product rating asynchronously after review is removed
        recalculate_product_rating.delay(product_id)

        return {"message": "Review deleted"}

    # TODO: Implement update_review() method
    #  - Validate review exists and is active
    #  - Check ownership (only author can edit)
    #  - Update comment and/or grade
    #  - Recalculate product rating after grade change
