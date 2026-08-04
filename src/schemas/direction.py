from pydantic import BaseModel, Field

from typing import Literal


class DirectionSchema(BaseModel):
    code: str = Field(..., description="Код направления (e.g. 09.03.04)")
    profile: str | None = Field(
        None, description="Профиль направления / Специализация (e.g. ИИ)"
    )
    education_form: Literal["full_time", "part_time", "distance"] = Field(
        ..., description="Форма обучения (e.g. Очная)"
    )
    funding_type: Literal[
        "budget", "paid", "commercial", "special_quota", "separate_quota", "target"
    ] = Field(..., description="Тип финансирования (e.g. Бюджет)")
