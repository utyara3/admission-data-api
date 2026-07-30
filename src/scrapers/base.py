from abc import ABC, abstractmethod
from typing import Any
from src.core.schemas import ContestListResponse


class BaseScraper(ABC):
    """Абстрактный класс для всех скраперов"""

    university_id: str

    @abstractmethod
    async def scrape(
        self, direction_code: str, education_form: str, funding_type: str, **kwargs: Any
    ) -> ContestListResponse:
        """
        Основной метод парсинга.

        Args:
            direction_code: Код направления (09.03.04)
            education_form: Форма обучения (full_time, part_time)
            funding_type: Тип финансирования (budget, paid)
            **kwargs: Дополнительные параметры (зависит от вуза)

        Returns:
            ContestListResponse: Стандартизированные данные
        """
        pass

    @abstractmethod
    async def get_available_directions(self) -> list[dict]:
        """Получить список доступных направлений для вуза"""
        pass
