from pydantic import BaseModel, Field


from .university import UniversitySchema
from .direction import DirectionSchema
from .applicant import ApplicantSchema

from src.core.enums import EducationDegree, EducationForm, FundingType


class ContestQueryParams(BaseModel):
    university: str = Field(..., description="ID вуза")
    education_degree: EducationDegree = Field(..., description="Уровень обучения")
    code: str = Field(..., description="Код направления")
    profile: str | None = Field(None, description="Профиль направления / Специализация")
    education_form: EducationForm = Field(..., description="Форма обучения")
    funding_type: FundingType = Field(..., description="Тип финансирования")


class ContestListResponse(BaseModel):
    university: UniversitySchema
    direction: DirectionSchema
    applicant: list[ApplicantSchema] = Field(
        ..., description="Список абитуриентов, участвующих в конкурсе"
    )
