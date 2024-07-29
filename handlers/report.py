from aiogram import Router, F,Bot
from handlers.States import States
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile,InputMediaPhoto, Message
from utils.callback import UserInfo
from base.base_conn import BotDB
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from keyboards.report import report_keyboard,exit_keyboard
from utils.captcha_generator.generator import selectRandomFruit
from configs.pictures import pictures_path,days
router = Router()

class CaptchaInfo:
    code:str | None = None
    fruit_name:str | None = None

@router.callback_query(UserInfo.filter(F.level == 6))
async def ReportCaptcha(call: CallbackQuery, callback_data: UserInfo, state: FSMContext):
    captcha = selectRandomFruit()
    CaptchaInfo.code = captcha[2]
    CaptchaInfo.fruit_name = captcha[0]
    BotDB.add_captcha_info(call.from_user.id,CaptchaInfo.code)
    await call.message.edit_media(media = InputMediaPhoto(media= FSInputFile(path= pictures_path[5]),caption = f'Выберите {CaptchaInfo.fruit_name},что бы отправить отчет'),
                                reply_markup = report_keyboard(stage = callback_data.stage,
                                                            course = callback_data.course,
                                                            group = callback_data.group,
                                                            day = callback_data.day)
                                                            )
    await state.set_state(States.report_captcha)
    await call.answer()


@router.callback_query(UserInfo.filter(F.level == 7))
async def sendReport(call: CallbackQuery,callback_data: UserInfo,bot:Bot, state = FSMContext):
    if BotDB.get_captcha(user_id=call.from_user.id) == callback_data.captcha:
        BotDB.add_report(user_id= call.from_user.id, username= call.from_user.username,group= callback_data.group,day = days[callback_data.day])
        await bot.send_message(chat_id = '-1002217232410', text = (f"Отчет (неверное расписание):\nОт кого: @{call.from_user.username}\nКурс: {callback_data.course}\nГруппа: {callback_data.group}\nДень: {days[callback_data.day]}"))
        path = pictures_path[6]
    else:
        path = pictures_path[7]
    await call.message.edit_media(media=InputMediaPhoto(media = FSInputFile(path=path),
                                                            caption='Нажмите на кнопку,что бы вернуться обратно.'),
                                                            reply_markup=exit_keyboard(stage=callback_data.stage,
                                                                                       course = callback_data.course,
                                                                                       group=callback_data.course,
                                                                                       day = callback_data.day))
    await state.set_state(States.report_send)
    await call.answer()