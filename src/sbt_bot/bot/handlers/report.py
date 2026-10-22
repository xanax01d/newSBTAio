from contextlib import suppress
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from sbt_bot.bot.callbacks import ReportCB
from sbt_bot.bot.keyboards import captcha_keyboard, report_back_keyboard
from sbt_bot.bot.states import ReportStates
from sbt_bot.config import Settings
from sbt_bot.db.repositories import ReportRepository
from sbt_bot.utils.captcha import generate_captcha
from sbt_bot.utils.week import DAYS_OF_WEEK

router = Router(name="report")


@router.callback_query(ReportCB.filter(F.action == "start"))
async def on_report_start(
    call: CallbackQuery,
    callback_data: ReportCB,
    state: FSMContext,
    settings: Settings,
) -> None:
    if call.message is None:
        return

    challenge = generate_captcha()
    await state.update_data(captcha_code=challenge.expected_code)
    await state.set_state(ReportStates.captcha)

    with suppress(TelegramBadRequest):
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(path=settings.picture_path(6)),
                caption=f"Выберите <b>{challenge.prompt_label}</b>, чтобы отправить отчёт:",
            ),
            reply_markup=captcha_keyboard(
                stage=callback_data.stage,
                course=callback_data.course,
                group=callback_data.group,
                day=callback_data.day,
            ),
        )
    await call.answer()


@router.callback_query(ReportCB.filter(F.action == "verify"))
async def on_report_verify(
    call: CallbackQuery,
    callback_data: ReportCB,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
    settings: Settings,
) -> None:
    if call.message is None:
        return

    fsm_data = await state.get_data()
    expected_code = fsm_data.get("captcha_code")
    await state.update_data(captcha_code=None)

    day_name = DAYS_OF_WEEK[callback_data.day] if 0 <= callback_data.day < 6 else "Неизвестно"

    if expected_code and expected_code == callback_data.captcha:
        await ReportRepository(session).create(
            user_id=call.from_user.id,
            username=call.from_user.username,
            group_name=callback_data.group,
            day_name=day_name,
        )
        if settings.report_chat_id is not None:
            username_part = (
                f"@{call.from_user.username}" if call.from_user.username else "без username"
            )
            first_name = escape(call.from_user.first_name or "")
            await bot.send_message(
                chat_id=settings.report_chat_id,
                text=(
                    "Отчёт (неверное расписание):\n"
                    f"От кого: {username_part} <i><b>({first_name})</b></i>\n"
                    f"Курс: {callback_data.course}\n"
                    f"Группа: {escape(callback_data.group)}\n"
                    f"День: {day_name}"
                ),
            )
        picture_idx = 7
        caption = "Отчёт отправлен! Нажмите на кнопку, чтобы вернуться обратно."
    else:
        picture_idx = 8
        caption = "Капча не пройдена. Нажмите на кнопку, чтобы вернуться обратно."

    with suppress(TelegramBadRequest):
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(path=settings.picture_path(picture_idx)),
                caption=caption,
            ),
            reply_markup=report_back_keyboard(
                stage=callback_data.stage,
                course=callback_data.course,
                group=callback_data.group,
                day=callback_data.day,
            ),
        )
    await state.set_state(ReportStates.sent)
    await call.answer()
