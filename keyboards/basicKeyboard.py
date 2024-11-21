from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from configs.levels import levels, courses
from utils.callback import UserInfo
from configs.groups import groupList1v, groupList2v, groupList3v, groupList4v, groupList1s, groupList2s, groupList3s, \
    groupList4s
from configs.forParse import days

def selectStage():
    """
    Function, used to create a markup of the keyboard, that appears when user write /start in chat with bot.
        Requires:
            Nothing.
        Returns:
            InlineKeyboardMarkup - markup of the keyboard.
    """
    keyboard_builder = InlineKeyboardBuilder()
    for stage in levels:
        keyboard_builder.button(text=stage, callback_data=UserInfo(stage=stage,
                                                                   course=None,
                                                                   group=None,
                                                                   day=None,
                                                                   level=1,
                                                                   captcha=None))
    keyboard_builder.button(text='Developer', url='tg://user?id=5504351206')
    keyboard_builder.adjust(2, 1)
    return keyboard_builder.as_markup()


def selectCourse(stage: str):
    """
    Function, that creates a markup of keyboard, when user selected the stage.
        Requires:
            stage:str - stage of education, that user selected.
        Returns:
            InlineKeyboardMarkup - markup of the keyboard.
    """
    keyboard_builder = InlineKeyboardBuilder()
    for course in courses:
        keyboard_builder.button(text=course, callback_data=UserInfo(stage=stage,
                                                                    course=course,
                                                                    group=None,
                                                                    day=None,
                                                                    level=2,
                                                                    captcha=None))
    keyboard_builder.button(text='Назад', callback_data=UserInfo(stage=stage,
                                                                 course='back',
                                                                 group=None,
                                                                 day=None,
                                                                 level=0,
                                                                 captcha=None))
    keyboard_builder.adjust(4,1)
    return keyboard_builder.as_markup()


def selectGroup(stage: str, course: str):
    """
    Function, that creates a markup of keyboard, when user selected the course.
        Requires:
            stage:str - stage of education, that user selected;
            course:str - course of education, that user selected.
        Returns:
            InlineKeyboardMarkup - markup of the keyboard.
    """
    keyboard_builder = InlineKeyboardBuilder()
    if stage == 'ВО':
        groupList = {
            '1 курc': groupList1v,
            '2 курc': groupList2v,
            '3 курc': groupList3v,
            '4 курc': groupList4v
        }
    elif stage == 'ССО':
        groupList = {
            '1 курc': groupList1s,
            '2 курc': groupList2s,
            '3 курc': groupList3s,
            '4 курc': groupList4s
        }
    for group in groupList.get(course):
        keyboard_builder.button(text=group, callback_data=UserInfo(stage=stage,
                                                                   course=course,
                                                                   group=group,
                                                                   day=None,
                                                                   level=3,
                                                                   captcha=None))
    keyboard_builder.button(text='Назад', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group='back',
                                                                 day=None,
                                                                 level=1,
                                                                 captcha=None))
    keyboard_builder.adjust(4)
    return keyboard_builder.as_markup()


def selectDay(stage:str, course:str, group:str):
    """
    Function, that creates a markup of keyboard, when user selected the group.
        Requires:
            stage:str - stage of education, that user selected;
            course:str - course of education, that user selected;
            group:str - group, that user selected.
        Returns:
            InlineKeyboardMarkup - markup of the keyboard.
    """
    keyboard_builder = InlineKeyboardBuilder()
    for day in days:
        keyboard_builder.button(text=day, callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=(days.index(day)),
                                                                 level=4,
                                                                 captcha=None))
    keyboard_builder.button(text='Назад', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=-1,
                                                                 level=2,
                                                                 captcha=None))
    keyboard_builder.adjust(3)
    return keyboard_builder.as_markup()


def selectDayNumeric(stage:str, course:str, group:str, day:int):
    """
    Function, that creates a markup of keyboard, when user selected the day.
        Requires:
            stage:str - stage of education, that user selected;
            course:str - course of education, that user selected;
            group:str - group, that user selected.
            day:int - number of the day, that user selected (0-6)
        Returns:
            markup:InlineKeyboardMarkup - markup of the keyboard.
    """
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='<<-', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=0,
                                                                 level=4,
                                                                 captcha=None))
    keyboard_builder.button(text='<-', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=day-1,
                                                                 level=4,
                                                                 captcha=None))
    keyboard_builder.button(text=days[day], callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=day,
                                                                 level=4,
                                                                 captcha=None))
    keyboard_builder.button(text='->', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=day+1,
                                                                 level=4,
                                                                 captcha=None))
    keyboard_builder.button(text='->>', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=len(days)-1,
                                                                 level=4,
                                                                 captcha=None))
    keyboard_builder.button(text = 'Неверное расписание',callback_data = UserInfo(stage = stage,
                                                                                      course = course,
                                                                                      group = group,
                                                                                      day = day,
                                                                                      level = 6,
                                                                                      captcha=None))
    keyboard_builder.button(text='Назад', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=999,
                                                                 level=2,
                                                                 captcha=None))
    keyboard_builder.adjust(5,1,1)
    markup = keyboard_builder.as_markup()
    if day == 0:
        for i in range(2):
            markup.inline_keyboard[0].pop(0)
        keyboard_builder.adjust(3,1,1)
    elif day == (len(days)-1):
        for i in range(2):
            markup.inline_keyboard[0].pop(3)
        keyboard_builder.adjust(3,1,1)
    return markup


