from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

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


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    """
    Authenticate user and return a JWT access token.

    Accepts form fields:
        - username : user email address
        - password : plain-text password

    Returns:
        - access_token : signed JWT
        - token_type   : 'bearer'
    """
    # OAuth2PasswordRequestForm uses 'username' field for email by convention
    return await service.login(form_data.username, form_data.password)
