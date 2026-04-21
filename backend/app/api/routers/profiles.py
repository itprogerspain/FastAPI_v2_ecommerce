from fastapi import APIRouter, Depends

from app.api.deps import get_profile_service, get_current_user
from app.application.profiles.schemas import Profile as ProfileSchema, ProfileUpdate
from app.application.profiles.service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=ProfileSchema)
async def get_my_profile(
    current_user=Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    """
    Return the current user's profile.
    A blank profile is created automatically if the user has none yet.
    """
    return await service.get_or_create_profile(current_user.id)


@router.put("/me", response_model=ProfileSchema)
async def update_my_profile(
    data: ProfileUpdate,
    current_user=Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    """
    Update the current user's profile.
    Only the fields included in the request body are changed.
    """
    return await service.update_profile(current_user.id, data)
