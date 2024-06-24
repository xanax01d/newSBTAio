from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from configs.levels import levels, courses
from utils.callback import UserInfo
from configs.groups import groupList1v, groupList2v, groupList3v, groupList4v, groupList1s, groupList2s, groupList3s, \
    groupList4s
from configs.forParse import days

def selectStage():
    keyboard_builder = InlineKeyboardBuilder()
    for stage in levels:
        keyboard_builder.button(text=stage, callback_data=UserInfo(stage=stage,
                                                                   course=None,
                                                                   group=None,
                                                                   day=None,
                                                                   level=1))
    keyboard_builder.button(text='Developer', url='tg://user?id=5504351206')
    keyboard_builder.adjust(2, 1);
    return keyboard_builder.as_markup()


def selectCourse(stage: str):
    keyboard_builder = InlineKeyboardBuilder()
    for course in courses:
        keyboard_builder.button(text=course, callback_data=UserInfo(stage=stage,
                                                                    course=course,
                                                                    group=None,
                                                                    day=None,
                                                                    level=2))
    keyboard_builder.button(text='Назад', callback_data=UserInfo(stage=stage,
                                                                 course='back',
                                                                 group=None,
                                                                 day=None,
                                                                 level=0))
    keyboard_builder.adjust(4,1);
    return keyboard_builder.as_markup()


def selectGroup(stage: str, course: str):
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
                                                                   level=3))
    keyboard_builder.button(text='Назад', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group='back',
                                                                 day=None,
                                                                 level=1))
    keyboard_builder.adjust(4);
    return keyboard_builder.as_markup()


def selectDay(stage, course, group):
    keyboard_builder = InlineKeyboardBuilder()
    for day in days:
        keyboard_builder.button(text=day, callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=(days.index(day)),
                                                                 level=4))
    keyboard_builder.button(text='Назад', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=-1,
                                                                 level=2))
    keyboard_builder.adjust(3)
    return keyboard_builder.as_markup()


def selectDayNumeric(stage, course, group,day):
    keyboard_builder = InlineKeyboardBuilder()
    #buttons
    keyboard_builder.button(text='<<-', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=0,
                                                                 level=4))
    keyboard_builder.button(text='<-', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=day-1,
                                                                 level=4))
    keyboard_builder.button(text=days[day], callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=day,
                                                                 level=4))
    keyboard_builder.button(text='->', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=day+1,
                                                                 level=4))
    keyboard_builder.button(text='->>', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=len(days)-1,
                                                                 level=4))
    keyboard_builder.button(text='Назад', callback_data=UserInfo(stage=stage,
                                                                 course=course,
                                                                 group=group,
                                                                 day=999,
                                                                 level=2))
    keyboard_builder.adjust(5)
    markup = keyboard_builder.as_markup()
    #check day
    if day == 0:
        #print('бимбим') #sonymanetov was here
        for i in range(2):
            markup.inline_keyboard[0].pop(0)
        keyboard_builder.adjust(3)
    elif day == (len(days)-1):
        #print('бамбам') #sonymanetov was here
        for i in range(2):
            markup.inline_keyboard[0].pop(3)
        keyboard_builder.adjust(3)
    return markup
    
