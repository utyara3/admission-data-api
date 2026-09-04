from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from src.core.database import Base
from src.core.enums import ApplicantContestStatus

if TYPE_CHECKING:
    from src.models.direction import Direction
    from src.models.applicant import Applicant
    from src.models.snapshot import Snapshot


class Application(Base):
    __tablename__ = "applications"

    applicant_db_id: Mapped[int] = mapped_column(
        ForeignKey("applicants.id", ondelete="CASCADE"), primary_key=True
    )
    direction_id: Mapped[int] = mapped_column(
        ForeignKey("directions.id", ondelete="CASCADE"), primary_key=True
    )
    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("snapshots.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    score_for_ia: Mapped[int] = mapped_column()  # ia - individual achievements
    position: Mapped[int] = mapped_column()
    priority: Mapped[int] = mapped_column()
    has_original: Mapped[bool] = mapped_column()
    is_bvi: Mapped[bool] = mapped_column()
    status: Mapped[ApplicantContestStatus] = mapped_column()

    direction: Mapped["Direction"] = relationship(
        "Direction", back_populates="applications"
    )
    applicant: Mapped["Applicant"] = relationship(
        "Applicant", back_populates="applications"
    )
    snapshot: Mapped["Snapshot"] = relationship(
        "Snapshot", back_populates="applications"
    )
