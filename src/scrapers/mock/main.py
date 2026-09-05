import asyncio
import random

from src.core.enums import EducationDegree, EducationForm, FundingType
from src.core.logger_config import setup_logger
from src.schemas import (
    ApplicantSchema,
    ContestListResponse,
    DirectionSchema,
    UniversitySchema,
)
from src.scrapers.base_scraper import BaseScraper

from .config import config

logger = setup_logger(__name__)

MOCK_EXAM_SUBJECTS = [
    "rus",
    "math_base",
    "math_prof",
    "it",
    "phys",
    "chem",
    "bio",
    "hist",
]


class MockScraper(BaseScraper):
    university_id = config.university_id

    async def scrape(
        self,
        education_degree: EducationDegree,
        direction_code: str,
        profile: str | None,
        education_form: EducationForm,
        funding_type: FundingType,
        **kwargs,
    ) -> ContestListResponse:
        logger.info(
            f"[MOCK] Генерация тестовых данных: "
            f"{direction_code}/{education_degree}/{education_form}/{funding_type}"
        )

        count = random.randint(10, 30)
        subjects = random.sample(MOCK_EXAM_SUBJECTS, k=3)
        await asyncio.sleep(20)
        applicants = self._generate_applicants(count, subjects)

        return ContestListResponse(
            university=UniversitySchema(
                id=self.university_id,
                full_name=config.university_name,
                short_name=config.university_short_name,
            ),
            direction=DirectionSchema(
                code=direction_code,
                profile=profile,
                education_form=education_form,
                funding_type=funding_type,
                education_degree=education_degree,
            ),
            applicant=applicants,
        )

    def _generate_applicants(
        self, count: int, subjects: list[str]
    ) -> list[ApplicantSchema]:
        applicants = []
        for _ in range(count):
            exam_scores = {s: random.randint(40, 100) for s in subjects}
            ia_score = random.choice([0, 0, 0, 5, 10])
            total_score = sum(exam_scores.values()) + ia_score

            applicants.append(
                ApplicantSchema(
                    position=0,
                    applicant_id=random.randint(1_000_000, 9_999_999),
                    priority=random.randint(1, 5),
                    has_original=random.choice([True, False]),
                    is_bvi=random.random() < 0.1,
                    total_score=total_score,
                    ia_score=ia_score,
                    exam_scores=exam_scores,
                    status=random.choice(
                        [
                            "Участвует в конкурсе",
                            "Участвует в конкурсе",
                            "Участвует в конкурсе",
                            "Ожидание результатов испытаний",
                            "Передано в вуз",
                        ]
                    ),
                )
            )

        applicants.sort(key=lambda a: a.total_score, reverse=True)
        for i, a in enumerate(applicants, 1):
            a.position = i

        return applicants
