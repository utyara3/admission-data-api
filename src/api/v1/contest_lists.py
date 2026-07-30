from fastapi import APIRouter, Depends, HTTPException, status

from src.scrapers import registry
from src.core.schemas import ContestQueryParams

router = APIRouter()


@router.get("/universities", tags=["Universities"])
async def get_available_universities() -> list[dict]:
    return registry.list_universities()


@router.get(
    "/contest-lists",
    # response_model=ContestListResponse,
    tags=["Contest Lists"],
)
async def get_contest_lists(
    query_data: ContestQueryParams = Depends(),
):  # -> ContestListResponse:
    try:
        scraper = registry.get_scraper(query_data.university)
        res = await scraper.scrape(
            query_data.code, query_data.education_form, query_data.funding_type
        )
        return res
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)[:500]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка парсинга: {str(e)[:500]}",
        )
