from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

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
    Create a signed JWT access token with expiration.

    Expected keys in data:
        - sub  : user email (standard JWT subject claim)
        - role : user role ('buyer' or 'seller')
        - id   : user ID

    Expiration is added automatically based on ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
