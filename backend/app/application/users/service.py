import jwt
from fastapi import HTTPException, status

from app.application.users.schemas import UserCreate, User as UserSchema
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.infrastructure.repositories.user import UserRepository


class UserService:
    """
    Business logic layer for users (Asynchronous).
    Handles validation and delegates database operations to UserRepository.
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user_data: UserCreate) -> UserSchema:
        """
        Register a new user.

        - Checks email uniqueness
        - Hashes the password via SecretStr.get_secret_value()
        - Saves the user to the database
        """
        existing_user = await self.repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # .get_secret_value() is required because password is typed as SecretStr
        data = {
            "email": user_data.email,
            "hashed_password": hash_password(user_data.password.get_secret_value()),
            "role": user_data.role,
        }

        return await self.repository.create(data)

    async def login(self, email: str, password: str) -> dict:
        """
        Authenticate a user and return both access and refresh JWT tokens.

        - Looks up active user by email
        - Verifies password against stored hash
        - Returns access_token, refresh_token and token_type on success
        """
        user = await self.repository.get_active_by_email(email)

        # Check user existence and password in one step
        # to avoid leaking whether the email exists
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = {"sub": user.email, "role": user.role, "id": user.id}

        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type": "bearer",
        }

    async def refresh_token(self, old_refresh_token: str) -> dict:
        """
        Validate old refresh token and issue a new one.

        - Decodes and verifies the token signature and expiration
        - Checks that token_type is 'refresh' (not 'access')
        - Verifies that the user still exists and is active
        - Returns a new refresh token
        """
        # TODO: In production, implement refresh token rotation:
        #  - Store refresh tokens in DB (table: refresh_tokens)
        #  - Invalidate old token on use (set is_used=True)
        #  - If already-used token is received — revoke ALL user tokens (possible leak)
        #  - Consider using Redis with TTL for automatic expiration

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str | None = payload.get("sub")
            token_type: str | None = payload.get("token_type")

            # Reject if email is missing or token is not a refresh token
            if email is None or token_type != "refresh":
                raise credentials_exception

        except jwt.ExpiredSignatureError:
            raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception

        user = await self.repository.get_active_by_email(email)
        if user is None:
            raise credentials_exception

        new_refresh_token = create_refresh_token(
            data={"sub": user.email, "role": user.role, "id": user.id}
        )

        return {
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    async def get_new_access_token(self, refresh_token: str) -> dict:
        """
        Issue a new access token using a valid refresh token.

        - Decodes and verifies the refresh token signature and expiration
        - Checks that token_type is 'refresh' to prevent access token misuse
        - Verifies that the user still exists and is active
        - Returns a new access token (refresh token stays unchanged)
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str | None = payload.get("sub")
            token_type: str | None = payload.get("token_type")

            # Only refresh tokens are accepted here
            if email is None or token_type != "refresh":
                raise credentials_exception

        except jwt.ExpiredSignatureError:
            raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception

        user = await self.repository.get_active_by_email(email)
        if user is None:
            raise credentials_exception

        # Issue new access token only — refresh token remains unchanged
        new_access_token = create_access_token(
            data={"sub": user.email, "role": user.role, "id": user.id}
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }
