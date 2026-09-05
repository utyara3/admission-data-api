import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.application import Application
from src.repositories import (
    ApplicantRepository,
    ApplicationRepository,
    DirectionRepository,
    SnapshotRepository,
)
from src.schemas.applicant import ApplicantSchema
from src.schemas.contest import ContestKey, ContestListResponse

logger = logging.getLogger(__name__)


class AdmissionSyncService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.applicant_repo = ApplicantRepository(session)
        self.application_repo = ApplicationRepository(session)
        self.direction_repo = DirectionRepository(session)
        self.snapshot_repo = SnapshotRepository(session)

    async def get_contest_list_from_db(
        self, contest_key: ContestKey
    ) -> ContestListResponse | None:
        applications = await self.direction_repo.get_contest_list(contest_key)

        if not applications:
            return None

        direction = applications[0].direction
        university = direction.university

        applicant_schemas = []
        for app in applications:
            applicant = app.applicant
            applicant_schemas.append(
                ApplicantSchema(
                    position=app.position,
                    applicant_id=int(applicant.applicant_id),
                    priority=app.priority,
                    has_original=app.has_original,
                    is_bvi=app.is_bvi,
                    total_score=applicant.sum_of_scores,
                    ia_score=app.score_for_ia,
                    exam_scores=applicant.score_for_exams,
                    status=app.status.value,
                )
            )

        return ContestListResponse(
            university={
                "id": university.university_id,
                "full_name": university.full_name,
                "short_name": university.short_name,
            },
            direction={
                "code": direction.code,
                "profile": direction.profile,
                "education_form": direction.education_form.value,
                "funding_type": direction.funding_type.value,
                "education_degree": direction.education_degree.value,
            },
            applicant=applicant_schemas,
        )

    async def save_contest_list_to_db(self, data: ContestListResponse) -> None:
        university = await self.direction_repo.get_or_create_university(
            university_id=data.university.id,
            full_name=data.university.full_name,
            short_name=data.university.short_name,
        )

        direction = await self.direction_repo.get_or_create_direction(
            university_id=university.id,
            education_degree=data.direction.education_degree,
            code=data.direction.code,
            profile=data.direction.profile,
            education_form=data.direction.education_form,
            funding_type=data.direction.funding_type,
        )

        snapshot = await self.snapshot_repo.create_snapshot(direction.id)

        applicants_data = [
            {
                "applicant_id": str(app.applicant_id),
                "sum_of_scores": app.total_score,
                "score_for_exams": app.exam_scores,
            }
            for app in data.applicant
        ]

        await self.applicant_repo.bulk_upsert_applicants(applicants_data)

        applicant_ids = [str(app.applicant_id) for app in data.applicant]
        id_map = await self.applicant_repo.get_ids_by_applicant_ids(applicant_ids)

        applications = []
        for app in data.applicant:
            db_applicant_id = id_map.get(str(app.applicant_id))
            if db_applicant_id is None:
                logger.warning(f"Applicant {app.applicant_id} not found after upsert")
                continue

            applications.append(
                Application(
                    applicant_db_id=db_applicant_id,
                    direction_id=direction.id,
                    snapshot_id=snapshot.id,
                    score_for_ia=app.ia_score,
                    position=app.position,
                    priority=app.priority,
                    has_original=app.has_original,
                    is_bvi=app.is_bvi,
                    status=app.status,
                )
            )

        await self.application_repo.bulk_insert_applications(applications)
        await self.session.commit()
