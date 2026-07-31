import os
import importlib

from typing import Type
from pathlib import Path

from .base_scraper import BaseScraper


class ScraperRegistry:
    """Динамический реестр всех доступных скраперов"""

    def __init__(self):
        self._scrapers: dict[str, Type[BaseScraper]] = {}
        self._configs: dict[str, object] = {}
        self._load_all_scrappers()

    def _load_all_scrappers(self):
        """Автоматически находит и загружает все скраперы из папок"""

        scrapers_dir = Path(__file__).parent

        for item in scrapers_dir.iterdir():
            if (
                not item.is_dir()
                or item.name.startswith("_")
                or item.name.startswith(".")
            ):
                continue

            university_id = item.name

            main_file = item / "main.py"
            config_file = item / "config.py"

            if not main_file.exists():
                print(f"Папка {university_id} пропускается: нет main.py")
                continue
            if not config_file.exists():
                print(f"Папка {university_id} пропускается: нет config.py")
                continue

            try:
                module = importlib.import_module(
                    f".{university_id}", package="src.scrapers"
                )

                scraper_class = None
                for attr_name in dir(module):
                    if attr_name.endswith("Scraper"):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BaseScraper)
                            and attr != BaseScraper
                        ):
                            scraper_class = attr
                            break

                if not scraper_class:
                    raise ValueError(
                        f"В модуле {university_id} не найден класс скрапера."
                    )

                config = module.config

                self._scrapers[university_id] = scraper_class
                self._configs[university_id] = config

                print(
                    f"Загружен скрапер: {university_id} ({config.university_short_name})"
                )

            except Exception as e:
                print(f"Ошибка загрузки скрапера {university_id}: {str(e)[:500]}")

    def get_scraper(self, university_id: str) -> BaseScraper:
        """Получает экземпляр скрапера вуза"""
        if university_id not in self._scrapers:
            available = ", ".join(self._scrapers.keys())
            raise ValueError(
                f"Скрапер {university_id} не найден.Доступные: {available}"
            )

        return self._scrapers[university_id]()

    def get_config(self, university_id: str) -> object:
        """Получает конфиг вуза"""
        if university_id not in self._configs:
            raise ValueError(f"Неизвестный вуз: {university_id}")

        return self._configs[university_id]

    def list_universities(self) -> list[dict]:
        """Возвращает список всех доступных вузов с метаданными"""
        return [
            {
                "id": uid,
                "name": config.university_name,
                "short_name": config.university_short_name,
                "website": config.website_url,
                "description": config.description,
            }
            for uid, config in self._configs.items()
        ]

    @property
    def available_ids(self) -> list[str]:
        return list(self._scrapers.keys())


registry = ScraperRegistry()
