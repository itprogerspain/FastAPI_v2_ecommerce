from fastapi import APIRouter, Depends, status

from app.application.users.schemas import UserCreate, User as UserSchema
from app.application.users.service import UserService
from app.api.deps import get_user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """
    Register a new user with role 'buyer' or 'seller'.
    Returns the created user without the password.
    """
    return await service.create_user(user_data)
