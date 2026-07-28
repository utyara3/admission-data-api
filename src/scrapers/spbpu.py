import httpx

from src.core.schemas import ApplicantSchema, ContestListResponse, DirectionSchema, ApplicantSchema



async def get_spbpu_list(
    direction: DirectionSchema
) -> ContestListResponse
