from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.callback import UserInfo
from configs.captcha import smiles_callbacks
def report_keyboard(stage,course,group,day):
    '''
    Function, used to create keyboard on report state
    '''
    keyboard_builder = InlineKeyboardBuilder()
    for smile,callback in smiles_callbacks.items():
        keyboard_builder.button(text = smile,callback_data=UserInfo(stage=stage,
                                                                                course=course,
                                                                                group=group,
                                                                                day=day,
                                                                                level=7,
                                                                                captcha=callback))
    keyboard_builder.button(text = 'Назад',
                            callback_data= UserInfo(stage = stage,
                                                    course = course,
                                                    group = group,
                                                    day = day,
                                                    level = 4,
                                                    captcha= None))
    keyboard_builder.adjust(3,3,1)
    return keyboard_builder.as_markup()

def exit_keyboard(stage,course,group,day):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text = 'Назад',
                            callback_data= UserInfo(stage = stage,
                                                    course = course,
                                                    group = group,
                                                    day = day,
                                                    level = 4,
                                                    captcha= None))
    return keyboard_builder.as_markup()