from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

# Create a hashing context using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme — tells FastAPI where the login endpoint is located
# tokenUrl must match the full path including the /api/v1 prefix
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    The resulting hash includes the salt, algorithm identifier and work factor.
    Example output: $2b$12$<salt><hash>
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches the stored bcrypt hash.
    Bcrypt automatically extracts the salt from the hash for comparison.
    Returns True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Create a signed JWT access token with short expiration (30 minutes).

    Expected keys in data:
        - sub  : user email (standard JWT subject claim)
        - role : user role ('buyer', 'seller' or 'admin')
        - id   : user ID

    Adds token_type='access' to distinguish from refresh tokens.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update(
        {
            "exp": expire,
            "token_type": "access",
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create a signed JWT refresh token with long expiration (7 days).

    Uses the same payload (sub, role, id) as access token but:
        - Has a longer lifetime (7 days vs 30 minutes)
        - Has token_type='refresh' to prevent misuse as access token

    In production, refresh tokens should be stored in a database (e.g. Redis)
    with a unique ID to allow revocation (e.g. on logout).
    Here we use a stateless approach for simplicity.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update(
        {
            "exp": expire,
            "token_type": "refresh",
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
