import logging
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from sbt_bot.db.repositories import ParsedLessonDTO, ScheduleRepository
from sbt_bot.parser.base import ScheduleSource

logger = logging.getLogger(__name__)


class ScheduleSyncService:
    """Coordinates schedule sources and persists parsed lessons to PostgreSQL."""

    def __init__(
        self,
        *,
        sources: Sequence[ScheduleSource],
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.sources = sources
        self.session_factory = session_factory

    async def sync_all(self) -> tuple[int, int]:
        """Fetch lessons from all sources and atomically update the database."""
        collected: list[ParsedLessonDTO] = []
        for source in self.sources:
            try:
                lessons = await source.fetch_lessons()
                logger.info("Source %s yielded %d lessons", source.name, len(lessons))
                collected.extend(lessons)
            except Exception:
                logger.exception("Schedule source %s failed", source.name)

        if not collected:
            logger.warning("No lessons collected from any source; keeping existing DB schedule")
            return 0, 0

        async with self.session_factory() as session:
            repo = ScheduleRepository(session)
            groups_count, entries_count = await repo.replace_schedule_entries(collected)
            logger.info(
                "Schedule sync complete: %d groups, %d entries saved",
                groups_count,
                entries_count,
            )
            return groups_count, entries_count
