from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DAYS_OF_WEEK: tuple[str, ...] = (
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
)

DAYS_ACCUSATIVE: tuple[str, ...] = (
    "Понедельник",
    "Вторник",
    "Среду",
    "Четверг",
    "Пятницу",
    "Субботу",
)

LESSON_TIMES: dict[int, str] = {
    1: "8:00 - 9:40",
    2: "9:55 - 11:35",
    3: "12:15 - 13:55",
    4: "14:10 - 15:50",
    5: "16:20 - 18:00",
    6: "18:15 - 19:55",
}


def get_current_week(
    dt: datetime | None = None,
    *,
    tz_name: str = "Europe/Minsk",
) -> int:
    """Calculate the current academic week number (1..4) starting from August 1."""
    if dt is None:
        now = datetime.now(ZoneInfo(tz_name)).replace(tzinfo=None)
    else:
        now = dt.replace(tzinfo=None)

    start_year = now.year if now.month >= 8 else now.year - 1
    first_day = datetime(start_year, 8, 1)

    if first_day.weekday() == 6:
        if now.month == 8 and now.day == 1:
            return 1
        start_week = first_day - timedelta(days=2)
        end_week = (first_day + timedelta(days=5)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
    else:
        weekday = first_day.weekday()
        start_week = first_day - timedelta(days=weekday)
        end_week = (first_day + timedelta(days=6 - weekday)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

    week = 1
    while not (start_week <= now <= end_week):
        start_week += timedelta(weeks=1)
        end_week += timedelta(weeks=1)
        week = 1 if week == 4 else week + 1
    return week


def resolve_day_and_week(
    *,
    offset_days: int = 0,
    dt: datetime | None = None,
    tz_name: str = "Europe/Minsk",
) -> tuple[int, int, bool]:
    """Return (day_of_week 0..5, week_number 1..4, shifted_from_sunday).

    If target date falls on Sunday (weekday == 6), shifts forward to Monday (0).
    """
    base = dt if dt is not None else datetime.now(ZoneInfo(tz_name))
    target = base + timedelta(days=offset_days)
    shifted = False
    if target.weekday() == 6:
        target += timedelta(days=1)
        shifted = True
    return target.weekday(), get_current_week(target, tz_name=tz_name), shifted
