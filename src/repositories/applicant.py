from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.applicant import Applicant


class ApplicantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_upsert_applicants(self, applicants_data: list[dict]) -> list[int]:
        if not applicants_data:
            return []

        stmt = insert(Applicant).values(applicants_data)

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[Applicant.applicant_id],
            set_={
                "sum_of_scores": stmt.excluded.sum_of_scores,
                "score_for_exams": stmt.excluded.score_for_exams,
            },
        )

        upsert_stmt = upsert_stmt.returning(Applicant.id)

        res = await self.session.execute(upsert_stmt)

        return list(res.scalars().all())

    async def get_ids_by_applicant_ids(
        self, applicant_ids: list[str]
    ) -> dict[str, int]:
        if not applicant_ids:
            return {}

        result = await self.session.execute(
            select(Applicant.applicant_id, Applicant.id).where(
                Applicant.applicant_id.in_(applicant_ids)
            )
        )
        return dict(result.all())
