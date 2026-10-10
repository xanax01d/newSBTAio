from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sbt_bot.bot.callbacks import MenuCB, ReportCB
from sbt_bot.utils.captcha import CAPTCHA_ITEMS


def captcha_keyboard(
    *,
    stage: str,
    course: int,
    group: str,
    day: int,
) -> InlineKeyboardMarkup:
    """Build fruit captcha keyboard for report verification."""
    builder = InlineKeyboardBuilder()
    for item in CAPTCHA_ITEMS:
        builder.button(
            text=item.emoji,
            callback_data=ReportCB(
                action="verify",
                stage=stage,
                course=course,
                group=group,
                day=day,
                captcha=item.code,
            ),
        )
    builder.button(
        text="⬅️ Отмена",
        callback_data=MenuCB(level=4, stage=stage, course=course, group=group, day=day),
    )
    builder.adjust(3, 3, 1)
    return builder.as_markup()


def report_back_keyboard(
    *,
    stage: str,
    course: int,
    group: str,
    day: int,
) -> InlineKeyboardMarkup:
    """Build return button after report submission."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Вернуться к расписанию",
        callback_data=MenuCB(level=4, stage=stage, course=course, group=group, day=day),
    )
    return builder.as_markup()
