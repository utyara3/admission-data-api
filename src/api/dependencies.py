from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.contest import ContestCache
from src.core.database import get_db
from src.core.redis_client import get_redis
from src.services.admission_sync import AdmissionSyncService


async def get_contest_cache() -> ContestCache:
    redis = get_redis()
    return ContestCache(redis)


async def get_admission_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdmissionSyncService:
    return AdmissionSyncService(db)
