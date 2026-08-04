from pydantic import BaseModel, Field

from typing import Literal

from .uviversity import UniversitySchema
from .direction import DirectionSchema
from .applicant import ApplicantSchema


class ContestQueryParams(BaseModel):
    university: str = Field(..., description="ID вуза")
    education_degree: Literal["bachelor", "specialist", "master", "postgraduate"] = (
        Field(..., description="Уровень обучения")
    )
    code: str = Field(..., description="Код направления")
    profile: str | None = Field(None, description="Профиль направления / Специализация")
    education_form: Literal["full_time", "part_time", "distance"] = Field(
        ..., description="Форма обучения"
    )
    funding_type: Literal[
        "budget", "paid", "commercial", "special_quota", "separate_quota", "target"
    ] = Field(..., description="Тип финансирования")


class ContestListResponse(BaseModel):
    university: UniversitySchema
    direction: DirectionSchema
    applicant: list[ApplicantSchema] = Field(
        ..., description="Список абитуриентов, участвующих в конкурсе"
    )
