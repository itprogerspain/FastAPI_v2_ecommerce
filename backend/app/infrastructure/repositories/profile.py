from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.profile import Profile as ProfileModel


class ProfileRepository:
    """
    Repository layer for profile database operations (Asynchronous).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> ProfileModel | None:
        """
        Retrieve a profile by the owner's user ID.
        Returns None if the user has no profile yet.
        """
        stmt = select(ProfileModel).where(ProfileModel.user_id == user_id).limit(1)
        result = await self.db.scalars(stmt)
        return result.first()

    async def create(self, user_id: int) -> ProfileModel:
        """
        Create a blank profile for the given user.
        All personal fields are left as None — the user fills them in later.
        """
        profile = ProfileModel(user_id=user_id)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update(self, profile: ProfileModel, data: dict) -> ProfileModel:
        """
        Apply a partial update to an existing profile.
        Only fields present in `data` are changed.
        """
        for field, value in data.items():
            setattr(profile, field, value)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
