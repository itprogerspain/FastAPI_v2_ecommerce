from decimal import Decimal
from fastapi import HTTPException, status

from app.infrastructure.repositories.order import OrderRepository
from app.infrastructure.repositories.product import ProductRepository
from app.infrastructure.repositories.cart import CartRepository
from app.models.db.order import Order as OrderModel, OrderItem as OrderItemModel


class OrderService:
    """
    Business logic for order creation and retrieval.
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        cart_repository: CartRepository,
        db_session,
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.cart_repository = cart_repository
        self.db = db_session

    async def _load_order_with_items(self, order_id: int) -> OrderModel | None:
        """
        Load order with items and products (delegates to repository).
        """
        return await self.order_repository.get_order_with_items(order_id)

    async def checkout(self, user_id: int) -> OrderModel:
        """
        Create an order from the user's cart.
        Validates stock, price, product availability.
        Deducts stock, creates order items, clears cart.
        """

        # 1. Load cart
        cart_items = await self.cart_repository.get_cart_items(user_id)
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty",
            )

        # 2. Create order
        order = OrderModel(user_id=user_id)
        total_amount = Decimal("0")

        # 3. Process each cart item
        for cart_item in cart_items:
            product = cart_item.product

            # Validate product
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {cart_item.product_id} is unavailable",
                )

            # Validate stock
            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for product {product.name}",
                )

            # Validate price
            if product.price is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {product.name} has no price set",
                )

            unit_price = product.price
            total_price = unit_price * cart_item.quantity
            total_amount += total_price

            # Create order item
            order_item = OrderItemModel(
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
            order.items.append(order_item)

            # Deduct stock
            product.stock -= cart_item.quantity

        # 4. Save order
        order.total_amount = total_amount
        await self.order_repository.create_order(order)

        # 5. Clear cart
        await self.cart_repository.clear_cart(user_id)

        # 6. Commit all changes
        await self.db.commit()

        # 7. Reload order with items
        created_order = await self._load_order_with_items(order.id)
        if not created_order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load created order",
            )

        return created_order

    async def list_orders(self, user_id: int, page: int, page_size: int):
        """
        Returns the current user's orders with simple pagination.

        """
        total = await self.order_repository.count_user_orders(user_id)
        items = await self.order_repository.list_user_orders(user_id, page, page_size)

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_order(self, user_id: int, order_id: int) -> OrderModel:
        """
        Returns detailed information about an order if it belongs to the user.

        """
        order = await self._load_order_with_items(order_id)

        if not order or order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        return order
