from fastapi import APIRouter, Depends, Response, status

from app.application.cart.schemas import (
    Cart as CartSchema,
    CartItem as CartItemSchema,
    CartItemCreate,
    CartItemUpdate,
)
from app.application.cart.service import CartService
from app.api.deps import get_cart_service
from app.core.deps import get_current_user
from app.models.db.user import User as UserModel

router = APIRouter(
    prefix="/cart",
    tags=["cart"],
)


@router.get(
    "/",
    response_model=CartSchema,
    status_code=status.HTTP_200_OK,
)
async def get_cart(
    service: CartService = Depends(get_cart_service),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Retrieve the current user's cart with all items and totals.
    total_quantity and total_price are calculated dynamically.
    """
    return await service.get_cart(user_id=current_user.id)


@router.post(
    "/items",
    response_model=CartItemSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_item_to_cart(
    payload: CartItemCreate,
    service: CartService = Depends(get_cart_service),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Add a product to the cart.
    If the product is already in the cart, its quantity is increased.
    """
    return await service.add_item(user_id=current_user.id, data=payload)


@router.put(
    "/items/{product_id}",
    response_model=CartItemSchema,
    status_code=status.HTTP_200_OK,
)
async def update_cart_item(
    product_id: int,
    payload: CartItemUpdate,
    service: CartService = Depends(get_cart_service),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Set a new quantity for an existing cart item.
    product_id is passed via URL path, quantity via request body.
    """
    return await service.update_item(
        user_id=current_user.id,
        product_id=product_id,
        data=payload,
    )


@router.delete(
    "/items/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_item_from_cart(
    product_id: int,
    service: CartService = Depends(get_cart_service),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Remove a specific product from the cart.
    Returns 204 No Content on success.
    """
    await service.remove_item(user_id=current_user.id, product_id=product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def clear_cart(
    service: CartService = Depends(get_cart_service),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Remove all items from the current user's cart.
    Returns 204 No Content on success.
    No error is raised if the cart is already empty.
    """
    await service.clear_cart(user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
