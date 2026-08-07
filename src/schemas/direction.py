from pydantic import BaseModel, Field

from src.core.enums import EducationForm, FundingType


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
