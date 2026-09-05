from pydantic import BaseModel, Field

from src.core.enums import EducationDegree, EducationForm, FundingType


class DirectionSchema(BaseModel):
    code: str = Field(..., description="Код направления (e.g. 09.03.04)")
    profile: str | None = Field(
        None, description="Профиль направления / Специализация (e.g. ИИ)"
    )
    education_form: EducationForm = Field(
        ..., description="Форма обучения (e.g. Очная)"
    )
    funding_type: FundingType = Field(
        ..., description="Тип финансирования (e.g. Бюджет)"
    )
    education_degree: EducationDegree = Field(
        default=EducationDegree.BACHELOR,
        description="Уровень обучения (e.g. bachelor)",
    )
