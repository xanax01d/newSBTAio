from collections.abc import Sequence

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sbt_bot.bot.callbacks import MenuCB, QuickCB, ReportCB
from sbt_bot.utils.week import DAYS_OF_WEEK

_DAY_SHORT: tuple[str, ...] = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб")


def stage_keyboard(
    stages: Sequence[str],
    *,
    saved_group: str | None = None,
) -> InlineKeyboardMarkup:
    """Build level 0 keyboard (education stage + quick actions if group is saved)."""
    builder = InlineKeyboardBuilder()
    if saved_group:
        builder.button(text="📅 Сегодня", callback_data=QuickCB(action="today"))
        builder.button(text="➡️ Завтра", callback_data=QuickCB(action="tomorrow"))
        builder.button(text="📆 Неделя", callback_data=QuickCB(action="week"))
        builder.adjust(3)

    stage_list = list(stages) if stages else ["ВО", "ССО"]
    for stage in stage_list:
        builder.button(
            text=stage,
            callback_data=MenuCB(level=1, stage=stage),
        )
    if saved_group:
        builder.adjust(3, len(stage_list))
    else:
        builder.adjust(len(stage_list))
    return builder.as_markup()


def course_keyboard(stage: str, courses: Sequence[int]) -> InlineKeyboardMarkup:
    """Build level 1 keyboard (course selection)."""
    builder = InlineKeyboardBuilder()
    course_list = list(courses) if courses else [1, 2, 3, 4]
    for course in course_list:
        builder.button(
            text=f"{course} курс",
            callback_data=MenuCB(level=2, stage=stage, course=course),
        )
    builder.button(text="⬅️ Назад", callback_data=MenuCB(level=0))
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def group_keyboard(
    stage: str,
    course: int,
    groups: Sequence[str],
) -> InlineKeyboardMarkup:
    """Build level 2 keyboard (group selection)."""
    builder = InlineKeyboardBuilder()
    for group in groups:
        builder.button(
            text=group,
            callback_data=MenuCB(level=3, stage=stage, course=course, group=group),
        )
    builder.adjust(2)
    builder.row()
    builder.button(
        text="⬅️ Назад",
        callback_data=MenuCB(level=1, stage=stage),
    )
    return builder.as_markup()


def day_keyboard(stage: str, course: int, group: str) -> InlineKeyboardMarkup:
    """Build level 3 keyboard (quick buttons + days of week)."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Сегодня", callback_data=QuickCB(action="today"))
    builder.button(text="➡️ Завтра", callback_data=QuickCB(action="tomorrow"))
    builder.button(text="📆 Неделя", callback_data=QuickCB(action="week"))

    for idx, day_name in enumerate(DAYS_OF_WEEK):
        builder.button(
            text=day_name,
            callback_data=MenuCB(
                level=4, stage=stage, course=course, group=group, day=idx
            ),
        )

    builder.button(
        text="⬅️ Назад",
        callback_data=MenuCB(level=2, stage=stage, course=course),
    )
    builder.adjust(3, 2, 2, 2, 1)
    return builder.as_markup()


def schedule_day_keyboard(
    *,
    stage: str,
    course: int,
    group: str,
    current_day: int,
) -> InlineKeyboardMarkup:
    """Build level 4 keyboard (day switcher + week + report + back)."""
    builder = InlineKeyboardBuilder()
    for idx, short in enumerate(_DAY_SHORT):
        label = f"• {short} •" if idx == current_day else short
        builder.button(
            text=label,
            callback_data=MenuCB(
                level=4, stage=stage, course=course, group=group, day=idx
            ),
        )
    builder.button(text="📆 Вся неделя", callback_data=QuickCB(action="week"))
    builder.button(
        text="⚠️ Ошибка в расписании",
        callback_data=ReportCB(
            action="start",
            stage=stage,
            course=course,
            group=group,
            day=current_day,
        ),
    )
    builder.button(
        text="⬅️ Назад",
        callback_data=MenuCB(level=3, stage=stage, course=course, group=group),
    )
    builder.adjust(6, 1, 1, 1)
    return builder.as_markup()


def schedule_week_keyboard(stage: str, course: int, group: str) -> InlineKeyboardMarkup:
    """Build keyboard for full-week view."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Сегодня", callback_data=QuickCB(action="today"))
    builder.button(text="➡️ Завтра", callback_data=QuickCB(action="tomorrow"))
    builder.button(
        text="⬅️ К выбору дня",
        callback_data=MenuCB(level=3, stage=stage, course=course, group=group),
    )
    builder.adjust(2, 1)
    return builder.as_markup()
