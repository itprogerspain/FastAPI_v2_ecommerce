from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db.cart import CartItem as CartItemModel
from app.models.db.product import Product as ProductModel


class CartRepository:
    """
    Repository layer for cart database operations (Asynchronous).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cart_items(self, user_id: int) -> list[CartItemModel]:
        """
        Retrieve all cart items for a user with product details eagerly loaded.
        Results are ordered by cart item id for stable display order.
        """
        stmt = (
            select(CartItemModel)
            .options(selectinload(CartItemModel.product))
            .where(CartItemModel.user_id == user_id)
            .order_by(CartItemModel.id)
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_cart_item(
        self, user_id: int, product_id: int
    ) -> CartItemModel | None:
        """
        Retrieve a single cart item by user_id and product_id.
        Eagerly loads the related product to avoid N+1 queries.
        Returns None if not found.
        """
        stmt = (
            select(CartItemModel)
            .options(selectinload(CartItemModel.product))
            .where(
                CartItemModel.user_id == user_id,
                CartItemModel.product_id == product_id,
            )
        )
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_product(self, product_id: int) -> ProductModel | None:
        """
        Retrieve an active product by ID.
        Used to validate product availability before cart operations.
        """
        stmt = (
            select(ProductModel)
            .where(
                ProductModel.id == product_id,
                ProductModel.is_active.is_(True),
            )
            .limit(1)
        )
        result = await self.db.scalars(stmt)
        return result.first()

    async def add_or_update_item(
        self, user_id: int, product_id: int, quantity: int
    ) -> CartItemModel:
        """
        Add a product to the cart or increase its quantity if already present.
        After commit, re-fetches the item to return fresh data with product loaded.
        """
        cart_item = await self.get_cart_item(user_id, product_id)

        if cart_item:
            # Item already in cart — increase quantity
            cart_item.quantity += quantity
        else:
            # New item — create cart record
            cart_item = CartItemModel(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
            )
            self.db.add(cart_item)

        await self.db.commit()

        # Re-fetch to get updated data with product relationship loaded
        return await self.get_cart_item(user_id, product_id)

    async def update_item_quantity(
        self, cart_item: CartItemModel, quantity: int
    ) -> CartItemModel:
        """
        Set a new quantity for an existing cart item.
        Re-fetches after commit to return fresh data with product loaded.
        """
        cart_item.quantity = quantity
        await self.db.commit()

        # Re-fetch to get updated data with product relationship loaded
        return await self.get_cart_item(cart_item.user_id, cart_item.product_id)

    async def delete_item(self, cart_item: CartItemModel) -> None:
        """
        Delete a single cart item from the database.
        """
        await self.db.delete(cart_item)
        await self.db.commit()

    async def clear_cart(self, user_id: int) -> None:
        """
        Delete all cart items for a user in a single SQL statement.
        """
        await self.db.execute(
            delete(CartItemModel).where(CartItemModel.user_id == user_id)
        )
        await self.db.commit()
