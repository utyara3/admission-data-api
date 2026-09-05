from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.snapshot import Snapshot


class SnapshotRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_snapshot(self, direction_id: int) -> Snapshot:
        """Создает новый снапшот для направления"""
        snapshot = Snapshot(direction_id=direction_id)
        self.session.add(snapshot)
        await self.session.flush()
        return snapshot

    async def get_latest_snapshot_id(self, direction_id: int) -> int | None:
        """Возвращает id последнего снапшота для направления"""
        res = await self.session.execute(
            select(Snapshot.id)
            .where(Snapshot.direction_id == direction_id)
            .order_by(desc(Snapshot.id))
            .limit(1)
        )
        return res.scalar_one_or_none()
