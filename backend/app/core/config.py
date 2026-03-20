import os
from dotenv import load_dotenv

load_dotenv()

# Secret key for JWT signing (loaded from .env)
SECRET_KEY = os.getenv("SECRET_KEY")

# JWT signing algorithm (symmetric — same key for sign and verify)
ALGORITHM = "HS256"

# Access token lifetime in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30
