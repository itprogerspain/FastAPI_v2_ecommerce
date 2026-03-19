from passlib.context import CryptContext

# Create a hashing context using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
