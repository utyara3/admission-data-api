from pydantic import BaseModel, Field


class UniversitySchema(BaseModel):
    id: str = Field(..., description="Уникальный ID вуза (e.g. spbpu)")
    full_name: str = Field(
        ...,
        description="Полное название вуза "
        "(e.g. Санкт Петербургский Политехнический Универститет)",
    )
    short_name: str = Field(..., description="Короткое название вуза (e.g. СПБПУ)")
