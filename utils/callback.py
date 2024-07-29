from aiogram.filters.callback_data import CallbackData

class UserInfo(CallbackData, prefix='UserInfo', sep='|'):
    '''
    Class for collecting information about user selection in bot
    '''
    stage: str | None = None #Stage that user selected
    course: str | None = None #Course that user selected
    group: str | None = None #Group that user selected
    day: int | None = None #Day that user selected
    level: int | None = 0 #Level of menu (really)
    captcha:str | None = None #for captcha