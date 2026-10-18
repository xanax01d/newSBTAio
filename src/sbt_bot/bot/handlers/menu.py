from contextlib import suppress
from html import escape

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from sbt_bot.bot.callbacks import MenuCB, QuickCB
from sbt_bot.bot.keyboards import (
    course_keyboard,
    day_keyboard,
    group_keyboard,
    schedule_day_keyboard,
    schedule_week_keyboard,
    stage_keyboard,
)
from sbt_bot.bot.states import MenuStates
from sbt_bot.config import Settings
from sbt_bot.db.repositories import ScheduleRepository, UserRepository
from sbt_bot.utils.formatting import format_day_schedule, format_week_schedule
from sbt_bot.utils.week import get_current_week, resolve_day_and_week

router = Router(name="menu")


@router.callback_query(MenuCB.filter(F.level == 0))
async def on_select_stage(
    call: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if call.message is None:
        return

    user_repo = UserRepository(session)
    sched_repo = ScheduleRepository(session)
    user = await user_repo.upsert(
        user_id=call.from_user.id,
        username=call.from_user.username,
        first_name=call.from_user.first_name,
        chat_id=call.message.chat.id,
    )
    stages = await sched_repo.list_stages()

    caption = "<b>Выберите ступень образования:</b>"
    if user.selected_group:
        caption = (
            f"Ваша сохранённая группа: <b>{escape(user.selected_group)}</b>\n"
            "Используйте быстрые кнопки или выберите ступень образования:"
        )

    with suppress(TelegramBadRequest):
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(path=settings.picture_path(1), filename="First_step.png"),
                caption=caption,
            ),
            reply_markup=stage_keyboard(stages, saved_group=user.selected_group),
        )
    await state.set_state(MenuStates.stage)
    await call.answer()


@router.callback_query(MenuCB.filter(F.level == 1))
async def on_select_course(
    call: CallbackQuery,
    callback_data: MenuCB,
    state: FSMContext,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if call.message is None:
        return

    await UserRepository(session).set_stage(call.from_user.id, callback_data.stage)
    courses = await ScheduleRepository(session).list_courses(callback_data.stage)

    with suppress(TelegramBadRequest):
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(path=settings.picture_path(2)),
                caption=f"Выбранная степень: <b><i>{escape(callback_data.stage)}</i></b>",
            ),
            reply_markup=course_keyboard(callback_data.stage, courses),
        )
    await state.set_state(MenuStates.course)
    await call.answer()


@router.callback_query(MenuCB.filter(F.level == 2))
async def on_select_group(
    call: CallbackQuery,
    callback_data: MenuCB,
    state: FSMContext,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if call.message is None:
        return

    await UserRepository(session).set_course(call.from_user.id, callback_data.course)
    groups = await ScheduleRepository(session).list_groups(
        callback_data.stage, callback_data.course
    )

    caption = f"Выбранный курс: <b><i>{callback_data.course} курс</i></b>"
    if not groups:
        caption += "\n\nГруппы для этого курса пока не загружены."

    with suppress(TelegramBadRequest):
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(path=settings.picture_path(3)),
                caption=caption,
            ),
            reply_markup=group_keyboard(callback_data.stage, callback_data.course, groups),
        )
    await state.set_state(MenuStates.group)
    await call.answer()


@router.callback_query(MenuCB.filter(F.level == 3))
async def on_select_day(
    call: CallbackQuery,
    callback_data: MenuCB,
    state: FSMContext,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if call.message is None:
        return

    await UserRepository(session).set_group(call.from_user.id, callback_data.group)

    with suppress(TelegramBadRequest):
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(path=settings.picture_path(4)),
                caption=f"Выбранная группа: <b><i>{escape(callback_data.group)}</i></b>",
            ),
            reply_markup=day_keyboard(
                callback_data.stage, callback_data.course, callback_data.group
            ),
        )
    await state.set_state(MenuStates.day)
    await call.answer()


@router.callback_query(MenuCB.filter(F.level == 4))
async def on_show_day_schedule(
    call: CallbackQuery,
    callback_data: MenuCB,
    state: FSMContext,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if call.message is None:
        return

    user_repo = UserRepository(session)
    sched_repo = ScheduleRepository(session)

    group_name = callback_data.group
    if not group_name:
        user = await user_repo.get(call.from_user.id)
        group_name = user.selected_group if user and user.selected_group else ""

    if not group_name:
        await call.answer("Сначала выберите группу.", show_alert=True)
        return

    week_num = callback_data.week or get_current_week(tz_name=settings.timezone)
    entries = await sched_repo.get_day_schedule(
        group_name=group_name,
        week_number=week_num,
        day_of_week=callback_data.day,
    )
    caption = format_day_schedule(
        entries,
        day_of_week=callback_data.day,
        week_number=week_num,
        group_name=group_name,
    )

    with suppress(TelegramBadRequest):
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(path=settings.picture_path(5)),
                caption=caption,
            ),
            reply_markup=schedule_day_keyboard(
                stage=callback_data.stage,
                course=callback_data.course,
                group=group_name,
                current_day=callback_data.day,
            ),
        )
    await state.set_state(MenuStates.schedule)
    await call.answer()


@router.callback_query(QuickCB.filter(F.action.in_({"today", "tomorrow"})))
async def on_quick_day(
    call: CallbackQuery,
    callback_data: QuickCB,
    state: FSMContext,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if call.message is None:
        return

    user = await UserRepository(session).get(call.from_user.id)
    if user is None or not user.selected_group:
        await call.answer("Сначала выберите группу.", show_alert=True)
        return

    offset = 1 if callback_data.action == "tomorrow" else 0
    day_idx, week_num, shifted = resolve_day_and_week(
        offset_days=offset, tz_name=settings.timezone
    )
    note = "Воскресенье — показано расписание на понедельник." if shifted else None

    entries = await ScheduleRepository(session).get_day_schedule(
        group_name=user.selected_group,
        week_number=week_num,
        day_of_week=day_idx,
    )
    caption = format_day_schedule(
        entries,
        day_of_week=day_idx,
        week_number=week_num,
        group_name=user.selected_group,
        note=note,
    )

    with suppress(TelegramBadRequest):
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(path=settings.picture_path(5)),
                caption=caption,
            ),
            reply_markup=schedule_day_keyboard(
                stage=user.selected_stage or "ВО",
                course=user.selected_course or 1,
                group=user.selected_group,
                current_day=day_idx,
            ),
        )
    await state.set_state(MenuStates.schedule)
    await call.answer()


@router.callback_query(QuickCB.filter(F.action == "week"))
async def on_quick_week(
    call: CallbackQuery,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if call.message is None:
        return

    user = await UserRepository(session).get(call.from_user.id)
    if user is None or not user.selected_group:
        await call.answer("Сначала выберите группу.", show_alert=True)
        return

    week_num = get_current_week(tz_name=settings.timezone)
    entries = await ScheduleRepository(session).get_week_schedule(
        group_name=user.selected_group,
        week_number=week_num,
    )
    text = format_week_schedule(
        entries,
        week_number=week_num,
        group_name=user.selected_group,
    )

    await call.message.answer(
        text=text,
        reply_markup=schedule_week_keyboard(
            stage=user.selected_stage or "ВО",
            course=user.selected_course or 1,
            group=user.selected_group,
        ),
    )
    await call.answer()
