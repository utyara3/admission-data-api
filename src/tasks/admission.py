import asyncio
import logging

from redis.asyncio import Redis

from src.cache.contest import ContestCache
from src.core.config import settings
from src.core.database import new_session
from src.core.enums import EducationDegree, EducationForm, FundingType
from src.schemas.contest import ContestKey
from src.scrapers import registry
from src.services.admission_sync import AdmissionSyncService
from src.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_contest_list(
    self,
    university_id: str,
    education_degree: str,
    code: str,
    profile: str | None,
    education_form: str,
    funding_type: str,
) -> dict:
    logger.info(
        f"Starting scrape for {university_id}: "
        f"{code}/{education_degree}/{education_form}/{funding_type}"
    )

    try:
        result = asyncio.run(
            _scrape_and_save(
                university_id=university_id,
                education_degree=education_degree,
                code=code,
                profile=profile,
                education_form=education_form,
                funding_type=funding_type,
            )
        )
        return result
    except ValueError:
        logger.error(
            f"Scrape failed: unknown university or bad params for {university_id}: {code}"
        )
        return {"status": "error", "university": university_id, "code": code}
    except Exception as e:
        logger.exception("Scrape failed")
        raise self.retry(exc=e)


async def _scrape_and_save(
    university_id: str,
    education_degree: str,
    code: str,
    profile: str | None,
    education_form: str,
    funding_type: str,
) -> dict:
    scraper = registry.get_scraper(university_id)

    data = await scraper.scrape(
        education_degree=EducationDegree(education_degree),
        direction_code=code,
        profile=profile,
        education_form=EducationForm(education_form),
        funding_type=FundingType(funding_type),
    )

    async with new_session() as session:
        service = AdmissionSyncService(session)
        await service.save_contest_list_to_db(data)

    await _invalidate_cache(
        university_id,
        education_degree,
        code,
        profile,
        education_form,
        funding_type,
    )

    logger.info(f"Scrape completed for {university_id}: {code}")
    return {"status": "ok", "university": university_id, "code": code}


async def _invalidate_cache(
    university_id: str,
    education_degree: str,
    code: str,
    profile: str | None,
    education_form: str,
    funding_type: str,
) -> None:
    try:
        key = ContestCache.make_key(
            ContestKey(
                university_id=university_id,
                education_degree=EducationDegree(education_degree),
                code=code,
                profile=profile,
                education_form=EducationForm(education_form),
                funding_type=FundingType(funding_type),
            )
        )

        redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        try:
            cache = ContestCache(redis)
            await cache.delete(key)
        finally:
            await redis.aclose()
    except Exception:
        logger.warning("Failed to invalidate cache", exc_info=True)


@celery_app.task
def scrape_all_universities() -> dict:
    logger.info("Periodic scrape task triggered")
    return {"status": "ok", "detail": "No contest keys configured for periodic sync"}
