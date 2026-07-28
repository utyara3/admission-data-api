from fastapi import APIRouter, Depends, HTTPException, status

from src.core.schemas import (
    UniversitySchema,
    ApplicantSchema,
    DirectionSchema,
    ContestListResponse,
)

from test import fetch

router = APIRouter()


@router.get("/university-list", response_model=ContestListResponse)
async def get_list(direction: DirectionSchema) -> ContestListResponse:
    url = "https://my.spbstu.ru/home/get-abit-list"
    params = {
        "filter_1": 2,
        "filter_2": 1,
        "filter_3": 649,
        "education_level": "bachelor",
    }

    req = await fetch(url, params)

