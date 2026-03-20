from fastapi import HTTPException, status

from app.application.users.schemas import UserCreate, User as UserSchema
from app.core.security import hash_password, verify_password, create_access_token
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

    async def login(self, email: str, password: str) -> dict:
        """
        Authenticate a user and return a JWT access token.

        - Looks up active user by email
        - Verifies password against stored hash
        - Returns access token and token type on success
        """
        # Find active user by email
        user = await self.repository.get_active_by_email(email)

        # Check user existence and password validity in one step
        # to avoid leaking whether the email exists
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create JWT with user identity data
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role, "id": user.id}
        )

        return {"access_token": access_token, "token_type": "bearer"}
