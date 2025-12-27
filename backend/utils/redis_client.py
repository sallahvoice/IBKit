import os

import redis
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from backend.utils.decorators import retry
from backend.utils.logger import get_logger

load_dotenv()
app = FastAPI()
logger = get_logger(__file__)

try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        password=os.getenv("REDIS_PASSWORD", None),
    )
    redis_client.ping()
    logger.info("Redis connection established")
except redis.exceptions.ConnectionError as e:
    logger.error(f"Redis connection failed: {e}")
    redis_client = None


@app.post("/expire_cache/")
async def expire_cache(request: Request):
    """
    Expires a cache key in Redis.

    Args:
        request (Request): FastAPI request object containing JSON with 'cache_key'.

    Returns:
        dict: Status and message about cache key deletion.
    """
    try:
        data = await request.json()
        cache_key = data.get("cache_key")
        if not cache_key:
            return {"status": "info", "message": "No cache_key provided"}
        if not redis_client:
            return {"status": "info", "message": "Redis client not available"}
        result = redis_client.delete(cache_key)
        if result:
            logger.info("Cache key '%s' expired successfully", cache_key)
            return {
                "status": "success",
                "message": f"Successfully deleted cache key: {cache_key}",
            }
        else:
            return {
                "status": "warning",
                "message": f"Failed to delete cache key: {cache_key}",
            }
    except redis.RedisError as e:
        logger.exception("Cache expiry error: %s", e)
        return {"status": "error", "message": f"Cache expiry failed: {str(e)}"}


@app.get("/health/")
def health():
    """
    Health check endpoint for Redis connection.

    Returns:
        dict: Status and Redis connection state.
    """
    redis_status = "connected" if redis_client else "disconnected"
    return {"status": "health", "message": redis_status}
