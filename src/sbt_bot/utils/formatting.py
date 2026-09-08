from collections import defaultdict
from collections.abc import Sequence
from html import escape

from sbt_bot.db.models import ScheduleEntry
from sbt_bot.utils.week import DAYS_ACCUSATIVE, DAYS_OF_WEEK, LESSON_TIMES


def _format_lesson_group(entries: Sequence[ScheduleEntry]) -> str:
    first = entries[0]
    time_str = first.time_range or LESSON_TIMES.get(first.lesson_number, "")
    header = f"<b><i>{first.lesson_number} пара ({escape(time_str)})</i></b>"

    if len(entries) == 1 and entries[0].subgroup == 0:
        body = escape(entries[0].subject)
        extra = _format_extra(entries[0])
        return f"{header}\n{body}{extra}"

    parts = []
    for entry in entries:
        prefix = f"{entry.subgroup} п/г: " if entry.subgroup else ""
        parts.append(f"{prefix}{escape(entry.subject)}{_format_extra(entry)}")
    return f"{header}\n" + "\n".join(parts)


def _format_extra(entry: ScheduleEntry) -> str:
    details = []
    if entry.auditorium:
        details.append(f"ауд. {escape(entry.auditorium)}")
    if entry.teacher:
        details.append(escape(entry.teacher))
    return f" <i>({', '.join(details)})</i>" if details else ""


def format_day_schedule(
    entries: Sequence[ScheduleEntry],
    *,
    day_of_week: int,
    week_number: int,
    group_name: str,
    note: str | None = None,
) -> str:
    """Format a single day's schedule as Telegram HTML."""
    day_title = DAYS_ACCUSATIVE[day_of_week]
    lines = [
        f"<b>Расписание на <i>{day_title}</i></b> ({week_number} неделя) • "
        f"<b>{escape(group_name)}</b>",
    ]
    if note:
        lines.append(f"<i>{escape(note)}</i>")
    lines.append("")

    if not entries:
        lines.append("Пар нет.")
        return "\n".join(lines)

    by_lesson: dict[int, list[ScheduleEntry]] = defaultdict(list)
    for entry in entries:
        by_lesson[entry.lesson_number].append(entry)

    blocks = [_format_lesson_group(by_lesson[num]) for num in sorted(by_lesson)]
    lines.append("\n\n".join(blocks))
    return "\n".join(lines)


def format_week_schedule(
    entries: Sequence[ScheduleEntry],
    *,
    week_number: int,
    group_name: str,
) -> str:
    """Format a full week's schedule as Telegram HTML."""
    header = f"<b>Расписание на неделю ({week_number} неделя)</b> • <b>{escape(group_name)}</b>\n"
    if not entries:
        return f"{header}\nНа эту неделю пар не найдено."

    by_day: dict[int, list[ScheduleEntry]] = defaultdict(list)
    for entry in entries:
        by_day[entry.day_of_week].append(entry)

    day_blocks: list[str] = [header]
    for day_idx in range(len(DAYS_OF_WEEK)):
        day_entries = by_day.get(day_idx, [])
        day_name = DAYS_OF_WEEK[day_idx]
        if not day_entries:
            day_blocks.append(f"<b>📅 {day_name}</b>\nПар нет.")
            continue

        by_lesson: dict[int, list[ScheduleEntry]] = defaultdict(list)
        for entry in day_entries:
            by_lesson[entry.lesson_number].append(entry)

        lesson_lines = []
        for num in sorted(by_lesson):
            slot_entries = by_lesson[num]
            time_str = slot_entries[0].time_range or LESSON_TIMES.get(num, "")
            if len(slot_entries) == 1 and slot_entries[0].subgroup == 0:
                text = f"{escape(slot_entries[0].subject)}{_format_extra(slot_entries[0])}"
            else:
                text = " | ".join(
                    f"{f'{e.subgroup}п/г: ' if e.subgroup else ''}"
                    f"{escape(e.subject)}{_format_extra(e)}"
                    for e in slot_entries
                )
            lesson_lines.append(f"• <b>{num} пара</b> ({escape(time_str)}): {text}")

        day_blocks.append(f"<b>📅 {day_name}</b>\n" + "\n".join(lesson_lines))

    return "\n\n".join(day_blocks)
