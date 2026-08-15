from datetime import UTC, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sbt_bot.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    """Telegram user profile and saved group preferences."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    selected_stage: Mapped[str | None] = mapped_column(String(16), nullable=True)
    selected_course: Mapped[int | None] = mapped_column(Integer, nullable=True)
    selected_group: Mapped[str | None] = mapped_column(String(32), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )


class StudyGroup(Base):
    """Academic study group (e.g., ВО / 1 курс / СИ-391)."""

    __tablename__ = "study_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    stage: Mapped[str] = mapped_column(String(16), nullable=False)
    course: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    entries: Mapped[list["ScheduleEntry"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_study_groups_stage_course", "stage", "course"),)


class ScheduleEntry(Base):
    """Single lesson slot for a group, week, and day."""

    __tablename__ = "schedule_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..4
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Mon .. 5=Sat
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..7
    subgroup: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0=all, 1, 2

    time_range: Mapped[str] = mapped_column(String(32), nullable=False)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    auditorium: Mapped[str | None] = mapped_column(String(64), nullable=True)
    teacher: Mapped[str | None] = mapped_column(String(128), nullable=True)

    group: Mapped["StudyGroup"] = relationship(back_populates="entries")

    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "week_number",
            "day_of_week",
            "lesson_number",
            "subgroup",
            name="uq_schedule_slot",
        ),
        Index("ix_schedule_lookup", "group_id", "week_number", "day_of_week"),
    )


class Report(Base):
    """User-submitted schedule error report."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    group_name: Mapped[str] = mapped_column(String(32), nullable=False)
    day_name: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
