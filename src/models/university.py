from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.direction import Direction


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), unique=True)
    short_name: Mapped[str] = mapped_column(String(255), unique=True)
    university_id: Mapped[str] = mapped_column(String(255), unique=True)

    directions: Mapped[list["Direction"]] = relationship(
        "Direction", back_populates="university"
    )
