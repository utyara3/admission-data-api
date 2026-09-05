from src.scrapers import registry
from src.scrapers.base_scraper import BaseScraper


class TestScraperRegistry:
    def test_mock_scraper_loaded(self):
        assert "mock" in registry.available_ids

    def test_get_scraper_returns_instance(self):
        scraper = registry.get_scraper("mock")
        assert isinstance(scraper, BaseScraper)

    def test_get_nonexistent_scraper_raises(self):
        import pytest

        with pytest.raises(ValueError, match="не найден"):
            registry.get_scraper("nonexistent_university")

    def test_list_universities(self):
        universities = registry.list_universities()
        assert len(universities) >= 1
        mock_uni = next(u for u in universities if u["id"] == "mock")
        assert mock_uni["short_name"] == "ТестУн"

    def test_get_config(self):
        config = registry.get_config("mock")
        assert config.university_id == "mock"
        assert config.university_name == "Тестовый университет"

    def test_get_nonexistent_config_raises(self):
        import pytest

        with pytest.raises(ValueError):
            registry.get_config("nonexistent_university")
