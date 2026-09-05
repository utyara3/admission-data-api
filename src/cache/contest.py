from redis.asyncio import Redis

from src.core.config import settings
from src.schemas.contest import ContestKey, ContestListResponse


class ContestCache:
    PREFIX = "contest"

    def __init__(self, redis: Redis):
        self.redis = redis

    @classmethod
    def make_key(cls, contest_key: ContestKey) -> str:
        return ":".join(
            [
                cls.PREFIX,
                contest_key.university_id,
                contest_key.education_degree.value,
                contest_key.code,
                contest_key.profile or "",
                contest_key.education_form.value,
                contest_key.funding_type.value,
            ]
        )

    async def get(self, key: str) -> ContestListResponse | None:
        data = await self.redis.get(key)

        if data is None:
            return None

        return ContestListResponse.model_validate_json(data)

    async def set(
        self, key: str, data: ContestListResponse, ttl: int = settings.CACHE_TTL
    ) -> None:
        await self.redis.set(key, data.model_dump_json(), ex=ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
