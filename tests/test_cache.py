import pytest

from src.cache.contest import ContestCache
from src.core.enums import EducationDegree, EducationForm, FundingType
from src.schemas.applicant import ApplicantSchema
from src.schemas.contest import ContestKey, ContestListResponse
from src.schemas.direction import DirectionSchema
from src.schemas.university import UniversitySchema


@pytest.fixture
def contest_key() -> ContestKey:
    return ContestKey(
        university_id="mock",
        education_degree=EducationDegree.BACHELOR,
        code="09.03.04",
        profile=None,
        education_form=EducationForm.FULL_TIME,
        funding_type=FundingType.BUDGET,
    )


@pytest.fixture
def sample_response() -> ContestListResponse:
    return ContestListResponse(
        university=UniversitySchema(
            id="mock",
            full_name="Тестовый университет",
            short_name="ТестУн",
        ),
        direction=DirectionSchema(
            code="09.03.04",
            profile=None,
            education_form=EducationForm.FULL_TIME,
            funding_type=FundingType.BUDGET,
            education_degree=EducationDegree.BACHELOR,
        ),
        applicant=[
            ApplicantSchema(
                position=1,
                applicant_id=1234567,
                priority=1,
                has_original=True,
                is_bvi=False,
                total_score=277,
                ia_score=10,
                exam_scores={"rus": 91, "math_prof": 86, "it": 90},
                status="Участвует в конкурсе",
            ),
        ],
    )


class TestContestCacheMakeKey:
    def test_key_format(self, contest_key: ContestKey):
        key = ContestCache.make_key(contest_key)
        assert key == "contest:mock:bachelor:09.03.04::full_time:budget"

    def test_key_with_profile(self, contest_key: ContestKey):
        contest_key.profile = "ИИ"
        key = ContestCache.make_key(contest_key)
        assert key == "contest:mock:bachelor:09.03.04:ИИ:full_time:budget"


class TestContestCacheGetSet:
    async def test_set_and_get(
        self,
        cache: ContestCache,
        contest_key: ContestKey,
        sample_response: ContestListResponse,
    ):
        key = ContestCache.make_key(contest_key)
        await cache.set(key, sample_response)

        result = await cache.get(key)
        assert result is not None
        assert result.university.id == "mock"
        assert len(result.applicant) == 1
        assert result.applicant[0].applicant_id == 1234567

    async def test_get_miss(self, cache: ContestCache):
        result = await cache.get("contest:nonexistent")
        assert result is None

    async def test_delete(
        self,
        cache: ContestCache,
        contest_key: ContestKey,
        sample_response: ContestListResponse,
    ):
        key = ContestCache.make_key(contest_key)
        await cache.set(key, sample_response)
        await cache.delete(key)

        result = await cache.get(key)
        assert result is None

    async def test_ttl(
        self,
        cache: ContestCache,
        contest_key: ContestKey,
        sample_response: ContestListResponse,
    ):
        key = ContestCache.make_key(contest_key)
        await cache.set(key, sample_response, ttl=60)

        ttl = await cache.redis.ttl(key)
        assert 0 < ttl <= 60
