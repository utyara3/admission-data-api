from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import fakeredis.aioredis
import pytest
from httpx import ASGITransport, AsyncClient

from src.cache.contest import ContestCache
from src.core.database import get_db
from src.main import app


@pytest.fixture
async def fake_redis() -> AsyncGenerator[fakeredis.aioredis.FakeRedis, None]:
    server = fakeredis.aioredis.FakeServer()
    redis = fakeredis.aioredis.FakeRedis(server=server, decode_responses=True)
    yield redis
    await redis.aclose()


@pytest.fixture
def cache(fake_redis: fakeredis.aioredis.FakeRedis) -> ContestCache:
    return ContestCache(fake_redis)


@pytest.fixture
async def client(
    fake_redis: fakeredis.aioredis.FakeRedis,
) -> AsyncGenerator[AsyncClient, None]:
    mock_session = AsyncMock()

    async def _override_get_db():
        yield mock_session

    async def _override_get_contest_cache():
        return ContestCache(fake_redis)

    from src.api.dependencies import get_contest_cache

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_contest_cache] = _override_get_contest_cache

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
