from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.infrastructure.db import get_async_db
from app.core.config import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer


from app.infrastructure.repositories.category import CategoryRepository
from app.application.categories.service import CategoryService
from app.infrastructure.repositories.product import ProductRepository
from app.application.products.service import ProductService
from app.infrastructure.repositories.user import UserRepository
from app.application.users.service import UserService
from app.infrastructure.repositories.review import ReviewRepository
from app.application.reviews.service import ReviewService
from app.infrastructure.repositories.cart import CartRepository
from app.application.cart.service import CartService
from app.infrastructure.repositories.order import OrderRepository
from app.application.orders.service import OrderService
from app.infrastructure.repositories.profile import ProfileRepository
from app.application.profiles.service import ProfileService
from app.infrastructure.repositories.message import MessageRepository
from app.application.messages.service import MessageService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")


async def get_category_service(
    db: AsyncSession = Depends(get_async_db),
) -> CategoryService:
    """
    Dependency that provides CategoryService instance using an async session.
    """
    repository = CategoryRepository(db)
    return CategoryService(repository)


async def get_product_service(
    db: AsyncSession = Depends(get_async_db),
) -> ProductService:
    """
    Dependency that provides ProductService instance using an async session.
    """
    product_repository = ProductRepository(db)
    category_repository = CategoryRepository(db)

    return ProductService(
        product_repository,
        category_repository,
    )


async def get_user_service(
    db: AsyncSession = Depends(get_async_db),
) -> UserService:
    """
    Dependency that provides UserService instance using an async session.
    """
    repository = UserRepository(db)
    return UserService(repository)


async def get_review_service(
    db: AsyncSession = Depends(get_async_db),
) -> ReviewService:
    """
    Dependency that provides ReviewService instance using an async session.
    """
    review_repository = ReviewRepository(db)
    product_repository = ProductRepository(db)

    return ReviewService(
        review_repository,
        product_repository,
    )


async def get_cart_service(
    db: AsyncSession = Depends(get_async_db),
) -> CartService:
    """
    Dependency that provides CartService instance using an async session.
    """
    repository = CartRepository(db)
    return CartService(repository)


async def get_order_service(
    db: AsyncSession = Depends(get_async_db),
) -> OrderService:
    order_repo = OrderRepository(db)
    product_repo = ProductRepository(db)
    cart_repo = CartRepository(db)

    return OrderService(
        order_repository=order_repo,
        product_repository=product_repo,
        cart_repository=cart_repo,
        db_session=db,
    )


async def get_profile_service(
    db: AsyncSession = Depends(get_async_db),
) -> ProfileService:
    """
    Dependency that provides ProfileService instance using an async session.
    """
    repository = ProfileRepository(db)
    return ProfileService(repository)


async def get_message_service(
    db: AsyncSession = Depends(get_async_db),
) -> MessageService:
    """
    Dependency that provides MessageService instance using an async session.
    """
    repository = MessageRepository(db)
    return MessageService(repository)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Extract current user from JWT access token.
    Validates signature, expiration and user existence.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int | None = payload.get("id")

        if user_id is None:
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_active_by_email(payload.get("sub"))

    if user is None:
        raise credentials_exception

    return user
