from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove,FSInputFile
from aiogram.filters import Command
from keyboards.basicKeyboard import selectStage
from base.base_conn import BotDB
from aiogram.fsm.context import FSMContext
from handlers.States import States
from configs.pictures import pictures_path
router = Router()

@router.message(Command('start'))
async def start(message:Message,state:FSMContext):
    reply_markup=ReplyKeyboardRemove()
    await message.answer_photo(
        caption="<b>Выберите ступень образования:</b> ",
        parse_mode="HTML",
        reply_markup=selectStage(),
        photo= FSInputFile(path = pictures_path[0],filename='First_step.png')
    )
    BotDB.add_user_info(message.from_user.id,
                        message.from_user.username,
                        message.from_user.first_name,
                        message.chat.id)
    await state.set_state(States.stage)

@router.message(Command('sendLogs'))
async def sendLogs(message:Message):
    if message.from_user.id == 5504351206:
        await message.reply_document(FSInputFile('log.txt'))
    else:
        await message.reply(text = 'У вас недостаточно полномочий!')
    print(message.chat.id)