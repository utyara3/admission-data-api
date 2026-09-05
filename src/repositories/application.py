from sqlalchemy.ext.asyncio import AsyncSession

from src.models.application import Application


class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_insert_applications(self, applications: list[Application]) -> None:
        self.session.add_all(applications)
