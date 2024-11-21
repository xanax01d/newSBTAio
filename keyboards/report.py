import random

from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.callback import UserInfo
from configs.captcha import smiles_callbacks

def report_keyboard(stage:str,course:str,group:str,day:int):
    """
    Function, used to create keyboard on report state
    Requires:
        stage:str - stage of User's education
        course:str - course of User
        group:str - group, where user is study
        day:int - day
    Returns:
        InlineKeyboardMarkup - Keyboard markup with buttons for captcha
    """
    keys = list(smiles_callbacks.keys())
    random.shuffle(keys)
    shuffled_smiles_callbacks = dict()
    for key in keys:
        shuffled_smiles_callbacks.update({key:smiles_callbacks[key]})
    keyboard_builder = InlineKeyboardBuilder()
    for smile,callback in shuffled_smiles_callbacks.items():
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
    """
    Function, used to create an exit button after captcha
    Requires:
        stage:str - stage of User's education
        course:str - course of User
        group:str - group, where user is study
        day:int - day
    Returns:
        InLineKeyboardMarkup- Keyboard markup with button "Назад" ("Back")
    """
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text = 'Назад',
                            callback_data= UserInfo(stage = stage,
                                                    course = course,
                                                    group = group,
                                                    day = day,
                                                    level = 4,
                                                    captcha= None))
    return keyboard_builder.as_markup()