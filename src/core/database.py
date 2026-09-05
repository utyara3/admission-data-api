from sqlalchemy import pool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, pool_size=5, max_overflow=10)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase): ...


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def new_session() -> AsyncSession:
    """Create a fresh session with a new engine for Celery tasks.

    The global engine pool is bound to the event loop that created it.
    Celery tasks run in asyncio.run() which creates a new loop, so we
    need a fresh engine with NullPool to avoid 'attached to different loop'.
    """
    temp_engine = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)
    factory = async_sessionmaker(
        temp_engine, class_=AsyncSession, expire_on_commit=False
    )
    return factory()
