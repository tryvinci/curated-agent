import redis
from app.core.config import get_settings

settings = get_settings()

# Redis connection
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses=True
)


def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    return redis_client


def check_redis_connection() -> bool:
    """Check if Redis is connected and responsive"""
    try:
        redis_client.ping()
        return True
    except redis.ConnectionError:
        return False