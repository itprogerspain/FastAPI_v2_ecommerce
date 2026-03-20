from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.user import User as UserModel


class UserRepository:
    """
    Repository layer for user database operations (Asynchronous).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> UserModel | None:
        """
        Retrieve a user by email address regardless of active status.
        Returns None if not found.
        """
        stmt = select(UserModel).where(UserModel.email == email).limit(1)
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_active_by_email(self, email: str) -> UserModel | None:
        """
        Retrieve an active user by email address.
        Returns None if not found or user is inactive.
        """
        stmt = (
            select(UserModel)
            .where(UserModel.email == email, UserModel.is_active.is_(True))
            .limit(1)
        )
        result = await self.db.scalars(stmt)
        return result.first()

    async def create(self, data: dict) -> UserModel:
        """
        Create a new user in the database.
        """
        user = UserModel(**data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
