from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from keyboards.basicKeyboard import selectStage
from base.base_conn import BotDB
from aiogram.fsm.context import FSMContext
from handlers.States import States
router = Router()
@router.message(Command('start'))
async def start(message:Message,state:FSMContext):
    reply_markup=ReplyKeyboardRemove()
    await message.answer(
    "<b>Выберите ступень образования:</b> ",
        parse_mode="HTML",
        reply_markup=selectStage()
    )
    BotDB.add_user_info(message.from_user.id,
                        message.from_user.username,
                        message.from_user.first_name,
                        message.chat.id)
    await state.set_state(States.stage)