from redis.asyncio import ConnectionPool, Redis

from src.core.config import settings

_pool: ConnectionPool | None = None


async def init_redis() -> None:
    global _pool

    _pool = ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        max_connections=20,
    )


async def close_redis() -> None:
    global _pool

    if _pool is not None:
        await _pool.aclose()
        _pool = None


def get_redis() -> Redis:
    global _pool

    if _pool is None:
        _pool = ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            max_connections=20,
        )

    return Redis(connection_pool=_pool, decode_responses=True)
