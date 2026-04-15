import os
from dotenv import load_dotenv

load_dotenv()

# Secret key for JWT signing (loaded from .env)
SECRET_KEY = os.getenv("SECRET_KEY")

# JWT signing algorithm (symmetric — same key for sign and verify)
ALGORITHM = "HS256"

# Access token lifetime in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Refresh token lifetime in days
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Redis URL for Celery broker and result backend (loaded from .env)
# Format: redis://host:port/db_number
# db 0 is used by default — can separate broker/backend by using db 1, db 2 etc.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# SMTP settings for sending emails via Celery tasks (loaded from .env)
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "E-Commerce Shop")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
