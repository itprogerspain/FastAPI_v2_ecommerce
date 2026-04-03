from decimal import Decimal

from fastapi import HTTPException, status

from app.application.cart.schemas import (
    Cart as CartSchema,
    CartItemCreate,
    CartItemUpdate,
    CartItem as CartItemSchema,
)
from app.infrastructure.repositories.cart import CartRepository


class CartService:
    """
    Business logic layer for cart operations (Asynchronous).
    Handles validation and delegates database operations to CartRepository.
    """

    def __init__(self, repository: CartRepository):
        self.repository = repository

    async def _validate_product(self, product_id: int):
        """
        Validate that the product exists and is active.
        Raises 404 if not found or inactive.
        """
        product = await self.repository.get_product(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or inactive",
            )
        return product

    async def get_cart(self, user_id: int) -> CartSchema:
        """
        Retrieve the full cart for a user.
        Calculates total_quantity and total_price dynamically from cart items.

        Uses Decimal for price calculations to avoid float precision errors.
        """
        items = await self.repository.get_cart_items(user_id)

        total_quantity = sum(item.quantity for item in items)
        total_price = sum(
            Decimal(item.quantity)
            * (item.product.price if item.product.price is not None else Decimal("0"))
            for item in items
        ) or Decimal("0.00")

        return CartSchema(
            user_id=user_id,
            items=items,
            total_quantity=total_quantity,
            total_price=total_price,
        )

    async def add_item(self, user_id: int, data: CartItemCreate) -> CartItemSchema:
        """
        Add a product to the cart or increase its quantity if already present.
        Validates product availability before adding.
        """
        await self._validate_product(data.product_id)
        return await self.repository.add_or_update_item(
            user_id=user_id,
            product_id=data.product_id,
            quantity=data.quantity,
        )

    async def update_item(
        self, user_id: int, product_id: int, data: CartItemUpdate
    ) -> CartItemSchema:
        """
        Set a new quantity for an existing cart item.
        Validates product availability and cart item existence.
        """
        await self._validate_product(product_id)

        cart_item = await self.repository.get_cart_item(user_id, product_id)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found",
            )

        return await self.repository.update_item_quantity(cart_item, data.quantity)

    async def remove_item(self, user_id: int, product_id: int) -> None:
        """
        Remove a specific product from the cart.
        Raises 404 if the item is not in the cart.
        """
        cart_item = await self.repository.get_cart_item(user_id, product_id)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found",
            )
        await self.repository.delete_item(cart_item)

    async def clear_cart(self, user_id: int) -> None:
        """
        Remove all items from the user's cart.
        No error is raised if the cart is already empty.
        """
        await self.repository.clear_cart(user_id)
