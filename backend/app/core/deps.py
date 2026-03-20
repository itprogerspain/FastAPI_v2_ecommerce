import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import SECRET_KEY, ALGORITHM
from app.core.security import oauth2_scheme
from app.infrastructure.db import get_async_db
from app.infrastructure.repositories.user import UserRepository
from app.models.db.user import User as UserModel


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> UserModel:
    """
    Dependency that validates the JWT token and returns the current active user.

    Raises 401 Unauthorized if:
        - Token is missing or malformed
        - Token has expired
        - 'sub' claim (email) is missing in payload
        - User not found in database or is inactive
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    # Use repository to stay consistent with project architecture
    repository = UserRepository(db)
    user = await repository.get_active_by_email(email)

    if user is None:
        raise credentials_exception

    return user


async def get_current_seller(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Dependency that ensures the current user has the 'seller' role.

    Raises 403 Forbidden if the user is not a seller.
    """
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can perform this action",
        )
    return current_user


async def get_current_admin(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Dependency that ensures the current user has the 'admin' role.

    Raises 403 Forbidden if the user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action",
        )
    return current_user
