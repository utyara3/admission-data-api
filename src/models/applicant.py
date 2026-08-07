from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from typing import TYPE_CHECKING

from src.core.database import Base
from src.core.enums import ExamSubject

if TYPE_CHECKING:
    from src.models.application import Application


class Applicant(Base):
    __tablename__ = "applicants"

    id: Mapped[int] = mapped_column(primary_key=True)
    applicant_id: Mapped[str] = mapped_column(String(20), unique=True)
    sum_of_scores: Mapped[int] = mapped_column()
    score_for_ia: Mapped[int] = mapped_column()  # ia - individual achievements
    score_for_exams: Mapped[dict[ExamSubject, int]] = mapped_column(JSONB)

    applications: Mapped[list["Application"]] = relationship(
        "Application", cascade="all, delete-orphan"
    )
