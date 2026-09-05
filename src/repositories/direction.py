from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.application import Application
from src.models.direction import Direction
from src.models.snapshot import Snapshot
from src.models.university import University
from src.schemas.contest import ContestKey


class DirectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_university(
        self,
        university_id: str,
        full_name: str,
        short_name: str,
    ) -> University:
        result = await self.session.execute(
            select(University).where(University.university_id == university_id)
        )
        university = result.scalar_one_or_none()

        if university is None:
            university = University(
                university_id=university_id,
                full_name=full_name,
                short_name=short_name,
            )
            self.session.add(university)
            await self.session.flush()

        return university

    async def get_or_create_direction(
        self,
        university_id: int,
        education_degree,
        code: str,
        profile: str | None,
        education_form,
        funding_type,
    ) -> Direction:
        result = await self.session.execute(
            select(Direction).where(
                Direction.university_id == university_id,
                Direction.education_degree == education_degree,
                Direction.code == code,
                Direction.profile == profile,
                Direction.education_form == education_form,
                Direction.funding_type == funding_type,
            )
        )
        direction = result.scalar_one_or_none()

        if direction is None:
            direction = Direction(
                university_id=university_id,
                education_degree=education_degree,
                code=code,
                name=code,
                profile=profile,
                education_form=education_form,
                funding_type=funding_type,
            )
            self.session.add(direction)
            await self.session.flush()

        return direction

    async def get_direction_id(
        self,
        contest_key: ContestKey,
    ) -> int | None:
        result = await self.session.execute(
            select(Direction.id)
            .join(Direction.university)
            .where(
                University.university_id == contest_key.university_id,
                Direction.education_degree == contest_key.education_degree,
                Direction.code == contest_key.code,
                Direction.profile == contest_key.profile,
                Direction.education_form == contest_key.education_form,
                Direction.funding_type == contest_key.funding_type,
            )
        )

        return result.scalar_one_or_none()

    async def get_contest_list(
        self,
        contest_key: ContestKey,
    ) -> list[Application] | None:
        direction_id = await self.get_direction_id(contest_key)

        if direction_id is None:
            return None

        snapshot = await self.session.scalar(
            select(Snapshot)
            .where(Snapshot.direction_id == direction_id)
            .order_by(Snapshot.id.desc())
            .limit(1)
        )

        if snapshot is None:
            return None

        result = await self.session.execute(
            select(Application)
            .where(
                Application.direction_id == direction_id,
                Application.snapshot_id == snapshot.id,
            )
            .options(
                selectinload(Application.applicant),
                selectinload(Application.direction).selectinload(Direction.university),
            )
            .order_by(Application.position)
        )

        return list(result.scalars().all())
