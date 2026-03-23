from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.application.users.schemas import (
    UserCreate,
    User as UserSchema,
    RefreshTokenRequest,
)
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
    Register a new user with role 'buyer', 'seller' or 'admin'.
    Returns the created user without the password.
    """
    return await service.create_user(user_data)


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    """
    Authenticate user and return both access and refresh JWT tokens.

    Accepts form fields:
        - username : user email address
        - password : plain-text password

    Returns:
        - access_token  : short-lived JWT (30 minutes)
        - refresh_token : long-lived JWT (7 days)
        - token_type    : 'bearer'
    """
    return await service.login(form_data.username, form_data.password)


@router.post("/refresh-token")
async def refresh_token(
    body: RefreshTokenRequest,
    service: UserService = Depends(get_user_service),
):
    """
    Issue a new refresh token using a valid existing refresh token.

    Returns:
        - refresh_token : new long-lived JWT (7 days)
        - token_type    : 'bearer'
    """
    return await service.refresh_token(body.refresh_token)


@router.post("/access-token")
async def get_new_access_token(
    body: RefreshTokenRequest,
    service: UserService = Depends(get_user_service),
):
    """
    Issue a new access token using a valid refresh token.

    The refresh token is validated but NOT rotated — it stays unchanged.
    Use this endpoint when the access token has expired.

    Returns:
        - access_token : new short-lived JWT (30 minutes)
        - token_type   : 'bearer'
    """
    return await service.get_new_access_token(body.refresh_token)
