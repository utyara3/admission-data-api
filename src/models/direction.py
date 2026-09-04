from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.core.enums import EducationDegree, EducationForm, FundingType

if TYPE_CHECKING:
    from src.models.application import Application
    from src.models.university import University


class Direction(Base):
    __tablename__ = "directions"

    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(
        ForeignKey("universities.id", ondelete="CASCADE")
    )
    education_degree: Mapped[EducationDegree] = mapped_column()
    code: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(100))
    profile: Mapped[str | None] = mapped_column(String(100), default=None)
    education_form: Mapped[EducationForm] = mapped_column()
    funding_type: Mapped[FundingType] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    university: Mapped["University"] = relationship(
        "University", back_populates="directions"
    )
    applications: Mapped["Application"] = relationship(
        "Application", back_populates="direction", cascade="all, delete-orphan"
    )
