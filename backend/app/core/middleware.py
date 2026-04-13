import uuid
from pathlib import Path

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

# Log file location: backend/logs/info.log
_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

logger.add(
    _LOG_DIR / "info.log",
    format="Log: [{extra[log_id]}:{time} - {level} - {message}]",
    level="INFO",
    rotation="10 MB",    # create a new file when current reaches 10 MB
    retention="30 days", # delete logs older than 30 days
    enqueue=True,        # thread-safe async writing
)


async def log_middleware(request: Request, call_next):
    """
    Logs every HTTP request with a unique log_id for tracing.
    - 401/402/403/404 responses → WARNING
    - Unhandled exceptions     → ERROR + 500 response
    - All other responses      → INFO
    """
    log_id = str(uuid.uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to {request.url.path} failed with {response.status_code}")
            else:
                logger.info(f"Successfully accessed {request.url.path}")
        except Exception as ex:
            logger.error(f"Request to {request.url.path} failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)
        return response
