from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRootEndpoint:
    async def test_root(self, client: AsyncClient):
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": 200}


@pytest.mark.asyncio
class TestUniversitiesEndpoint:
    async def test_get_universities(self, client: AsyncClient):
        response = await client.get("/universities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        mock_uni = next(u for u in data if u["id"] == "mock")
        assert mock_uni["short_name"] == "ТестУн"


@pytest.mark.asyncio
class TestContestListsEndpoint:
    @patch(
        "src.api.v1.contest_lists.AdmissionSyncService.get_contest_list_from_db",
        new_callable=AsyncMock,
        return_value=None,
    )
    async def test_unknown_university_returns_404(
        self, mock_get_db, client: AsyncClient
    ):
        response = await client.get(
            "/contest-lists",
            params={
                "university": "nonexistent",
                "education_degree": "bachelor",
                "code": "09.03.04",
                "education_form": "full_time",
                "funding_type": "budget",
            },
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_invalid_education_degree_returns_422(self, client: AsyncClient):
        response = await client.get(
            "/contest-lists",
            params={
                "university": "mock",
                "education_degree": "invalid",
                "code": "09.03.04",
                "education_form": "full_time",
                "funding_type": "budget",
            },
        )
        assert response.status_code == 422

    async def test_missing_required_param_returns_422(self, client: AsyncClient):
        response = await client.get(
            "/contest-lists",
            params={
                "university": "mock",
            },
        )
        assert response.status_code == 422
