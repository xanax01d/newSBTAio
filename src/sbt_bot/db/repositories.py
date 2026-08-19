from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from sbt_bot.db.models import Report, ScheduleEntry, StudyGroup, User


@dataclass(frozen=True, slots=True)
class ParsedLessonDTO:
    """Normalized lesson record produced by a schedule parser."""

    group_name: str
    stage: str
    course: int
    week_number: int
    day_of_week: int
    lesson_number: int
    subgroup: int
    time_range: str
    subject: str
    auditorium: str | None = None
    teacher: str | None = None


class UserRepository:
    """Async data-access methods for Telegram users."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def upsert(
        self,
        *,
        user_id: int,
        username: str | None,
        first_name: str | None,
        chat_id: int | None,
    ) -> User:
        user = await self.session.get(User, user_id)
        if user is None:
            user = User(
                id=user_id,
                username=username,
                first_name=first_name,
                chat_id=chat_id,
            )
            self.session.add(user)
        else:
            user.username = username
            user.first_name = first_name
            user.chat_id = chat_id
        await self.session.commit()
        return user

    async def set_stage(self, user_id: int, stage: str) -> None:
        user = await self.session.get(User, user_id)
        if user is not None:
            user.selected_stage = stage
            await self.session.commit()

    async def set_course(self, user_id: int, course: int) -> None:
        user = await self.session.get(User, user_id)
        if user is not None:
            user.selected_course = course
            await self.session.commit()

    async def set_group(self, user_id: int, group_name: str) -> None:
        user = await self.session.get(User, user_id)
        if user is not None:
            user.selected_group = group_name
            await self.session.commit()

    async def is_banned(self, user_id: int) -> bool:
        stmt = select(User.is_banned).where(User.id == user_id)
        result = await self.session.scalar(stmt)
        return bool(result)

    async def set_ban(self, user_id: int, banned: bool) -> bool:
        user = await self.session.get(User, user_id)
        if user is None:
            return False
        user.is_banned = banned
        await self.session.commit()
        return True


class ScheduleRepository:
    """Async data-access methods for study groups and schedule entries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_stages(self) -> list[str]:
        stmt = (
            select(StudyGroup.stage)
            .where(StudyGroup.is_active.is_(True))
            .distinct()
            .order_by(StudyGroup.stage)
        )
        rows = await self.session.scalars(stmt)
        return list(rows)

    async def list_courses(self, stage: str) -> list[int]:
        stmt = (
            select(StudyGroup.course)
            .where(StudyGroup.stage == stage, StudyGroup.is_active.is_(True))
            .distinct()
            .order_by(StudyGroup.course)
        )
        rows = await self.session.scalars(stmt)
        return list(rows)

    async def list_groups(self, stage: str, course: int) -> list[str]:
        stmt = (
            select(StudyGroup.name)
            .where(
                StudyGroup.stage == stage,
                StudyGroup.course == course,
                StudyGroup.is_active.is_(True),
            )
            .order_by(StudyGroup.name)
        )
        rows = await self.session.scalars(stmt)
        return list(rows)

    async def get_day_schedule(
        self,
        *,
        group_name: str,
        week_number: int,
        day_of_week: int,
    ) -> Sequence[ScheduleEntry]:
        stmt = (
            select(ScheduleEntry)
            .join(StudyGroup)
            .where(
                StudyGroup.name == group_name,
                ScheduleEntry.week_number == week_number,
                ScheduleEntry.day_of_week == day_of_week,
            )
            .order_by(ScheduleEntry.lesson_number, ScheduleEntry.subgroup)
        )
        rows = await self.session.scalars(stmt)
        return list(rows)

    async def get_week_schedule(
        self,
        *,
        group_name: str,
        week_number: int,
    ) -> Sequence[ScheduleEntry]:
        stmt = (
            select(ScheduleEntry)
            .join(StudyGroup)
            .where(
                StudyGroup.name == group_name,
                ScheduleEntry.week_number == week_number,
            )
            .order_by(
                ScheduleEntry.day_of_week,
                ScheduleEntry.lesson_number,
                ScheduleEntry.subgroup,
            )
        )
        rows = await self.session.scalars(stmt)
        return list(rows)

    async def replace_schedule_entries(
        self,
        lessons: Sequence[ParsedLessonDTO],
    ) -> tuple[int, int]:
        """Atomically upsert groups and replace their schedule entries.

        Returns (groups_count, entries_count).
        """
        if not lessons:
            return 0, 0

        group_meta: dict[str, tuple[str, int]] = {}
        for item in lessons:
            group_meta[item.group_name] = (item.stage, item.course)

        existing_groups_stmt = select(StudyGroup).where(
            StudyGroup.name.in_(list(group_meta.keys()))
        )
        existing_groups = {
            g.name: g for g in (await self.session.scalars(existing_groups_stmt))
        }

        for name, (stage, course) in group_meta.items():
            if name in existing_groups:
                grp = existing_groups[name]
                grp.stage = stage
                grp.course = course
                grp.is_active = True
            else:
                grp = StudyGroup(name=name, stage=stage, course=course, is_active=True)
                self.session.add(grp)
                existing_groups[name] = grp

        await self.session.flush()

        target_group_ids = [g.id for g in existing_groups.values()]
        await self.session.execute(
            delete(ScheduleEntry).where(ScheduleEntry.group_id.in_(target_group_ids))
        )

        # Deduplicate by unique slot key in case PDF has repeated rows
        unique_entries: dict[tuple[int, int, int, int, int], ScheduleEntry] = {}
        for item in lessons:
            group_id = existing_groups[item.group_name].id
            key = (
                group_id,
                item.week_number,
                item.day_of_week,
                item.lesson_number,
                item.subgroup,
            )
            unique_entries[key] = ScheduleEntry(
                group_id=group_id,
                week_number=item.week_number,
                day_of_week=item.day_of_week,
                lesson_number=item.lesson_number,
                subgroup=item.subgroup,
                time_range=item.time_range,
                subject=item.subject,
                auditorium=item.auditorium,
                teacher=item.teacher,
            )

        self.session.add_all(unique_entries.values())
        await self.session.commit()
        return len(existing_groups), len(unique_entries)


class ReportRepository:
    """Async data-access methods for error reports."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: int,
        username: str | None,
        group_name: str,
        day_name: str,
    ) -> Report:
        report = Report(
            user_id=user_id,
            username=username,
            group_name=group_name,
            day_name=day_name,
        )
        self.session.add(report)
        await self.session.commit()
        return report
