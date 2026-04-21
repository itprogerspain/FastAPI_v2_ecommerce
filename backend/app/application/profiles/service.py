from app.application.profiles.schemas import Profile as ProfileSchema, ProfileUpdate
from app.infrastructure.repositories.profile import ProfileRepository


class ProfileService:
    """
    Business logic layer for user profiles (Asynchronous).
    Delegates database operations to ProfileRepository.
    """

    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    async def get_or_create_profile(self, user_id: int) -> ProfileSchema:
        """
        Return the user's profile, creating a blank one if it does not exist yet.
        This ensures every user always has a profile row.
        """
        profile = await self.repository.get_by_user_id(user_id)
        if profile is None:
            profile = await self.repository.create(user_id)
        return profile

    async def update_profile(self, user_id: int, data: ProfileUpdate) -> ProfileSchema:
        """
        Update the current user's profile with the provided fields.
        Creates a blank profile first if the user has never saved one.
        Only non-None values from the request are applied.
        """
        profile = await self.repository.get_by_user_id(user_id)
        if profile is None:
            profile = await self.repository.create(user_id)

        # Only update fields explicitly sent by the client (exclude_unset=True
        # prevents overwriting existing values with None for omitted fields).
        update_data = data.model_dump(exclude_unset=True)
        return await self.repository.update(profile, update_data)
