import pytest
from pydantic import ValidationError

from src.core.enums import EducationDegree, EducationForm, FundingType
from src.schemas.applicant import ApplicantSchema
from src.schemas.contest import ContestKey, ContestListResponse, ContestQueryParams
from src.schemas.direction import DirectionSchema
from src.schemas.university import UniversitySchema


class TestContestKey:
    def test_valid_key(self):
        key = ContestKey(
            university_id="mock",
            education_degree="bachelor",
            code="09.03.04",
            profile=None,
            education_form="full_time",
            funding_type="budget",
        )
        assert key.university_id == "mock"
        assert key.education_degree == EducationDegree.BACHELOR

    def test_invalid_education_degree(self):
        with pytest.raises(ValidationError):
            ContestKey(
                university_id="mock",
                education_degree="invalid",
                code="09.03.04",
                profile=None,
                education_form="full_time",
                funding_type="budget",
            )

    def test_invalid_education_form(self):
        with pytest.raises(ValidationError):
            ContestKey(
                university_id="mock",
                education_degree="bachelor",
                code="09.03.04",
                profile=None,
                education_form="invalid",
                funding_type="budget",
            )

    def test_invalid_funding_type(self):
        with pytest.raises(ValidationError):
            ContestKey(
                university_id="mock",
                education_degree="bachelor",
                code="09.03.04",
                profile=None,
                education_form="full_time",
                funding_type="invalid",
            )


class TestContestQueryParams:
    def test_valid_query(self):
        params = ContestQueryParams(
            university="mock",
            education_degree="bachelor",
            code="09.03.04",
            education_form="full_time",
            funding_type="budget",
        )
        assert params.university == "mock"
        assert params.profile is None

    def test_with_profile(self):
        params = ContestQueryParams(
            university="mock",
            education_degree="bachelor",
            code="09.03.04",
            profile="ИИ",
            education_form="full_time",
            funding_type="budget",
        )
        assert params.profile == "ИИ"

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            ContestQueryParams(
                university="mock",
            )


class TestContestListResponse:
    def test_valid_response(self):
        response = ContestListResponse(
            university=UniversitySchema(
                id="mock",
                full_name="Тестовый университет",
                short_name="ТестУн",
            ),
            direction=DirectionSchema(
                code="09.03.04",
                education_form="full_time",
                funding_type="budget",
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
        assert len(response.applicant) == 1
        assert response.university.id == "mock"


class TestApplicantSchema:
    def test_valid_applicant(self):
        applicant = ApplicantSchema(
            position=1,
            applicant_id=1234567,
            priority=1,
            has_original=True,
            is_bvi=False,
            total_score=277,
            ia_score=10,
            exam_scores={"rus": 91, "math_prof": 86, "it": 90},
            status="Участвует в конкурсе",
        )
        assert applicant.position == 1
        assert applicant.total_score == 277

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            ApplicantSchema(
                position=1,
            )


class TestUniversitySchema:
    def test_valid_university(self):
        uni = UniversitySchema(
            id="mock",
            full_name="Тестовый университет",
            short_name="ТестУн",
        )
        assert uni.id == "mock"


class TestDirectionSchema:
    def test_default_education_degree(self):
        direction = DirectionSchema(
            code="09.03.04",
            education_form="full_time",
            funding_type="budget",
        )
        assert direction.education_degree == EducationDegree.BACHELOR

    def test_with_profile(self):
        direction = DirectionSchema(
            code="09.03.04",
            profile="ИИ",
            education_form="full_time",
            funding_type="budget",
        )
        assert direction.profile == "ИИ"


class TestEnums:
    def test_education_degree_values(self):
        assert EducationDegree.BACHELOR == "bachelor"
        assert EducationDegree.MASTER == "master"

    def test_education_form_values(self):
        assert EducationForm.FULL_TIME == "full_time"
        assert EducationForm.PART_TIME == "part_time"

    def test_funding_type_values(self):
        assert FundingType.BUDGET == "budget"
        assert FundingType.PAID == "paid"
