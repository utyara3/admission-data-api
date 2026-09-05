from unittest.mock import AsyncMock, patch

import pytest

from src.tasks.admission import scrape_contest_list


class TestScrapeContestList:
    @patch("src.tasks.admission._scrape_and_save", new_callable=AsyncMock)
    def test_task_success(self, mock_scrape):
        mock_scrape.return_value = {
            "status": "ok",
            "university": "mock",
            "code": "09.03.04",
        }

        result = scrape_contest_list(
            university_id="mock",
            education_degree="bachelor",
            code="09.03.04",
            profile=None,
            education_form="full_time",
            funding_type="budget",
        )
        assert result["status"] == "ok"
        assert result["university"] == "mock"
        mock_scrape.assert_called_once()

    def test_unknown_university_returns_error(self):
        result = scrape_contest_list(
            university_id="nonexistent",
            education_degree="bachelor",
            code="09.03.04",
            profile=None,
            education_form="full_time",
            funding_type="budget",
        )
        assert result["status"] == "error"
        assert result["university"] == "nonexistent"

    @patch("src.tasks.admission._scrape_and_save", new_callable=AsyncMock)
    def test_task_retries_on_exception(self, mock_scrape):
        mock_scrape.side_effect = ConnectionError("DB down")

        with pytest.raises(ConnectionError):
            scrape_contest_list(
                university_id="mock",
                education_degree="bachelor",
                code="09.03.04",
                profile=None,
                education_form="full_time",
                funding_type="budget",
            )
