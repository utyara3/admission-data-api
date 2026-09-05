import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.api.dependencies import get_admission_service, get_contest_cache
from src.cache.contest import ContestCache
from src.schemas.contest import ContestKey, ContestListResponse, ContestQueryParams
from src.scrapers import registry
from src.services.admission_sync import AdmissionSyncService
from src.tasks.admission import scrape_contest_list

logger = logging.getLogger(__name__)

router = APIRouter()

SCRAPE_POLL_INTERVAL = 1.0
SCRAPE_POLL_ATTEMPTS = 5


@router.get("/universities", tags=["Universities"])
async def get_available_universities() -> list[dict]:
    return registry.list_universities()


@router.get(
    "/contest-lists",
    response_model=None,
    tags=["Contest Lists"],
)
async def get_contest_lists(
    query_data: Annotated[ContestQueryParams, Depends()],
    cache: Annotated[ContestCache, Depends(get_contest_cache)],
    service: Annotated[AdmissionSyncService, Depends(get_admission_service)],
) -> ContestListResponse | JSONResponse:
    contest_key = ContestKey(
        university_id=query_data.university,
        education_degree=query_data.education_degree,
        code=query_data.code,
        profile=query_data.profile,
        education_form=query_data.education_form,
        funding_type=query_data.funding_type,
    )

    cache_key = ContestCache.make_key(contest_key)

    try:
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
    except Exception:
        logger.warning("Redis unavailable, proceeding without cache", exc_info=True)

    try:
        db_data = await service.get_contest_list_from_db(contest_key)
    except Exception:
        logger.exception("Database error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    if db_data is not None:
        try:
            await cache.set(cache_key, db_data)
        except Exception:
            logger.warning("Failed to set cache", exc_info=True)
        return db_data

    if query_data.university not in registry.available_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"University '{query_data.university}' not found",
        )

    try:
        scrape_contest_list.delay(
            university_id=query_data.university,
            education_degree=query_data.education_degree.value,
            code=query_data.code,
            profile=query_data.profile,
            education_form=query_data.education_form.value,
            funding_type=query_data.funding_type.value,
        )
    except Exception:
        logger.exception("Failed to enqueue scrape task")

    for _ in range(SCRAPE_POLL_ATTEMPTS):
        await asyncio.sleep(SCRAPE_POLL_INTERVAL)
        try:
            db_data = await service.get_contest_list_from_db(contest_key)
        except Exception:  # noqa: BLE001
            break
        if db_data is not None:
            try:
                await cache.set(cache_key, db_data)
            except Exception:
                logger.warning("Failed to set cache", exc_info=True)
            return db_data

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "pending",
            "detail": "Data not available yet. Scrape task queued.",
        },
    )
