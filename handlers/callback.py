#импорты \\ imports
from aiogram import Router, F
from handlers.States import States
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.basicKeyboard import selectCourse, selectGroup, selectDay,selectStage,selectDayNumeric
from utils.callback import UserInfo
from base.base_conn import BotDB
from contextlib import suppress
from configs.forParse import days_titles,days
from aiogram.exceptions import TelegramBadRequest
#создаем роутер \\ creating a router
router = Router()
#выбор ступени образования \\ choosing the level of education \\ level of menu = 0
@router.callback_query(UserInfo.filter(F.level == 0))
async def SelectStage(call:CallbackQuery,callback_data:UserInfo,state:FSMContext):
    await call.message.edit_text("<b>Выберите ступень образования:</b> ",
                                    parse_mode="HTML",
                                    reply_markup=selectStage()
    )
    BotDB.add_user_info(call.from_user.id,
                        call.from_user.username,
                        call.from_user.first_name,
                        call.from_user.id)
    await state.set_state(States.stage)
    await call.answer()
#выбор курса \\ сhoosing a course \\ level of menu = 1
@router.callback_query(UserInfo.filter(F.level == 1))
async def SelectCourse(call: CallbackQuery, callback_data: UserInfo, state: FSMContext):
    BotDB.add_user_stage(call.from_user.id,
                         callback_data.stage)
    await call.message.edit_text(text=(f'<b>Выберите курс:</b>\nВыбранная степень: <b><i>{callback_data.stage}</i></b>'),
                                 reply_markup=selectCourse(stage=callback_data.stage))
    await state.set_state(States.course)
    await call.answer()

#выбор группы \\ group selection \\ level of menu = 2
@router.callback_query(UserInfo.filter(F.level == 2))
async def SelectGroup(call: CallbackQuery, callback_data: UserInfo, state: FSMContext):
    BotDB.add_user_course(call.from_user.id,
                          callback_data.course)
    await call.message.edit_text(
        text=(f'<b>Выберите группу:</b>\nВыбранный курс: <b><i>{callback_data.course}</i></b>'),
        reply_markup=selectGroup(stage=callback_data.stage,
                                 course=callback_data.course))
    await state.set_state(States.group)
    await call.answer()

#выбор дня \\ choosing the day \\ level of menu - 3
@router.callback_query(UserInfo.filter(F.level == 3))
async def SelectDay(call: CallbackQuery, callback_data: UserInfo, state: FSMContext):
    BotDB.add_user_group(call.from_user.id, callback_data.group)
    await call.message.edit_text(text=f'<b>Выберите день:</b>\nВыбранная группа: <b><i>{callback_data.group}</i></b>',
                                 reply_markup=selectDay(stage=callback_data.stage,
                                                        course=callback_data.course,
                                                        group=callback_data.group))
    await state.set_state(States.day)
    await call.answer()

#отправляем расписание на день \\ sending a schedule \\ level of menu = 5
@router.callback_query(UserInfo.filter(F.level == 4))
async def SendSchedule(call: CallbackQuery, callback_data: UserInfo, state: FSMContext):
    with suppress(TelegramBadRequest):
        await call.message.edit_text(text=f'{days_titles.get(days[callback_data.day])}'+f'{BotDB.get_schedule(
            day=callback_data.day,
            group=BotDB.get_user_group(call.from_user.id))}',
                                    reply_markup=selectDayNumeric(stage=callback_data.stage,
                                                            course=callback_data.course,
                                                            group=callback_data.group,
                                                            day = callback_data.day))
    await state.set_state(States.day)
    await call.answer()
