from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.contest import ContestListResponse, ContestQueryParams
from src.scrapers import registry

router = APIRouter()


@router.get("/universities", tags=["Universities"])
async def get_available_universities() -> list[dict]:
    return registry.list_universities()


@router.get(
    "/contest-lists",
    response_model=ContestListResponse,
    tags=["Contest Lists"],
)
async def get_contest_lists(
    query_data: ContestQueryParams = Depends(),
) -> ContestListResponse:
    try:
        scraper = registry.get_scraper(query_data.university)
        res = await scraper.scrape(
            education_degree=query_data.education_degree,
            direction_code=query_data.code,
            education_form=query_data.education_form,
            profile=query_data.profile,
            funding_type=query_data.funding_type,
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка парсинга: {e!s}",
        )
