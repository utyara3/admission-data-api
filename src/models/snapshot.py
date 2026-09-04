from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from datetime import datetime, UTC

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.application import Application


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    direction_id: Mapped[int] = mapped_column(
        ForeignKey("directions.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    applications: Mapped[list["Application"]] = relationship(
        "Application", back_populates="snapshot"
    )
