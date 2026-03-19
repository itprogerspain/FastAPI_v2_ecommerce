from pydantic import BaseModel, Field, ConfigDict, EmailStr, SecretStr


class UserCreate(BaseModel):
    """
    Schema for user registration.
    Used in POST /users/ requests.

    Password is typed as SecretStr to prevent accidental exposure in logs.
    Access the raw value via: user.password.get_secret_value()
    """

    email: EmailStr = Field(description="User email address")
    password: SecretStr = Field(
        min_length=8, description="Password (minimum 8 characters)"
    )
    role: str = Field(
        default="buyer",
        pattern="^(buyer|seller)$",
        description="User role: 'buyer' or 'seller'",
    )


class User(BaseModel):
    """
    Schema for returning user data in API responses.
    Password is intentionally excluded for security.
    """

    id: int
    email: EmailStr
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)
