from fastapi import HTTPException, status

from app.application.users.schemas import UserCreate, User as UserSchema
from app.core.security import hash_password
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
        # Check if email is already registered
        existing_user = await self.repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # Build data dict with hashed password
        # .get_secret_value() is required because password is typed as SecretStr
        data = {
            "email": user_data.email,
            "hashed_password": hash_password(user_data.password.get_secret_value()),
            "role": user_data.role,
        }

        return await self.repository.create(data)
