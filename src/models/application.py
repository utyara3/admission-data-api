from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from src.core.database import Base
from src.core.enums import ApplicantContestStatus

if TYPE_CHECKING:
    from src.models.direction import Direction
    from src.models.applicant import Applicant


class Application(Base):
    __tablename__ = "applications"

    applicant_db_id: Mapped[int] = mapped_column(
        ForeignKey("applicants.id"), primary_key=True
    )
    direction_id: Mapped[int] = mapped_column(
        ForeignKey("directions.id"), primary_key=True
    )
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
