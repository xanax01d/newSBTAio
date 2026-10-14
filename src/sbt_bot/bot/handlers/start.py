from html import escape

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from sbt_bot.bot.keyboards import (
    schedule_day_keyboard,
    schedule_week_keyboard,
    stage_keyboard,
)
from sbt_bot.bot.states import MenuStates
from sbt_bot.config import Settings
from sbt_bot.db.repositories import ScheduleRepository, UserRepository
from sbt_bot.parser.service import ScheduleSyncService
from sbt_bot.utils.formatting import format_day_schedule, format_week_schedule
from sbt_bot.utils.week import get_current_week, resolve_day_and_week

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if message.from_user is None:
        return

    user_repo = UserRepository(session)
    sched_repo = ScheduleRepository(session)

    user = await user_repo.upsert(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        chat_id=message.chat.id,
    )
    stages = await sched_repo.list_stages()

    caption = "<b>Выберите ступень образования:</b>"
    if user.selected_group:
        caption = (
            f"Ваша сохранённая группа: <b>{escape(user.selected_group)}</b>\n"
            "Используйте быстрые кнопки или выберите другую ступень образования:"
        )

    await message.answer_photo(
        photo=FSInputFile(path=settings.picture_path(1), filename="First_step.png"),
        caption=caption,
        reply_markup=stage_keyboard(stages, saved_group=user.selected_group),
    )
    await state.set_state(MenuStates.stage)


@router.message(Command("today", "tomorrow"))
async def cmd_quick_day(
    message: Message,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if message.from_user is None:
        return

    user = await UserRepository(session).get(message.from_user.id)
    if user is None or not user.selected_group:
        await message.answer("Сначала выберите группу через /start.")
        return

    offset = 1 if (message.text or "").startswith("/tomorrow") else 0
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
    await message.answer_photo(
        photo=FSInputFile(path=settings.picture_path(5)),
        caption=caption,
        reply_markup=schedule_day_keyboard(
            stage=user.selected_stage or "ВО",
            course=user.selected_course or 1,
            group=user.selected_group,
            current_day=day_idx,
        ),
    )


@router.message(Command("week"))
async def cmd_quick_week(
    message: Message,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if message.from_user is None:
        return

    user = await UserRepository(session).get(message.from_user.id)
    if user is None or not user.selected_group:
        await message.answer("Сначала выберите группу через /start.")
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
    await message.answer(
        text=text,
        reply_markup=schedule_week_keyboard(
            stage=user.selected_stage or "ВО",
            course=user.selected_course or 1,
            group=user.selected_group,
        ),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>Доступные команды:</b>\n"
        "/start — главное меню и выбор группы\n"
        "/today — расписание на сегодня\n"
        "/tomorrow — расписание на завтра\n"
        "/week — расписание на текущую неделю\n"
        "/help — справка"
    )


@router.message(Command("sync"))
async def cmd_sync(
    message: Message,
    settings: Settings,
    sync_service: ScheduleSyncService,
) -> None:
    if message.from_user is None or message.from_user.id not in settings.admin_ids:
        await message.reply("У вас недостаточно полномочий!")
        return

    status = await message.reply("Запускаю обновление расписания...")
    groups_count, entries_count = await sync_service.sync_all()
    await status.edit_text(
        f"Синхронизация завершена: групп — <b>{groups_count}</b>, пар — <b>{entries_count}</b>."
    )


@router.message(Command("sendlogs", "sendLogs"))
async def cmd_send_logs(message: Message, settings: Settings) -> None:
    if message.from_user is None or message.from_user.id not in settings.admin_ids:
        await message.reply("У вас недостаточно полномочий!")
        return

    if not settings.log_file.exists():
        await message.reply("Файл логов ещё не создан.")
        return

    await message.reply_document(FSInputFile(settings.log_file))
