from typing import Protocol

from sbt_bot.db.repositories import ParsedLessonDTO


class ScheduleSource(Protocol):
    """Interface for any schedule provider (PDF scraper, Google Sheets, etc.)."""

    name: str

    async def fetch_lessons(self) -> list[ParsedLessonDTO]:
        """Fetch and parse schedule entries into normalized DTOs."""
        ...
