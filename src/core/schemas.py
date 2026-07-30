from pydantic import BaseModel, Field

from typing import Literal


class UniversitySchema(BaseModel):
    id: str = Field(..., description="Уникальный ID вуза (e.g. spbpu)")
    full_name: str = Field(
        ...,
        description="Полное название вуза "
        "(e.g. Санкт Петербургский Политехнический Универститет)",
    )
    short_name: str = Field(..., description="Короткое название вуза (e.g. СПБПУ)")


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


class ApplicantSchema(BaseModel):
    position: int = Field(
        ..., description="Порядковый номер внутри конкурсного списка (e.g. 1)"
    )
    applicant_id: int = Field(
        ..., description="Уникальный ID абитуриента (e.g. 1730447)"
    )
    priority: int = Field(..., description="Приоритет направления (e.g. 1)")
    has_original: bool = Field(
        ..., description="Подан ли оригинал аттестата (e.g. False)"
    )
    is_bvi: bool = Field(
        ..., description="Поступает ли абитуриент без вступиительных испытаний"
    )
    total_score: int = Field(
        ..., description="Суммарный балл за эзкамены и ИД (e.g. 277)"
    )
    ia_score: int = Field(
        ..., description="Баллы за индивидуальные достижения (e.g. 10)"
    )
    exam_scores: dict[str, int] = Field(
        ..., description="Баллы за ЕГЭ (e.g. {'рус': 91, 'мат': 86, 'инф': 90})"
    )
    status: str = Field(
        ..., description="Текущий статус абитуриента (e.g. Участвует в конкурсе)"
    )


class ContestQueryParams(BaseModel):
    university: str = Field(..., description="ID вуза")
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
