from aiogram.filters.callback_data import CallbackData

class UserInfo(CallbackData, prefix='UserInfo', sep='|'):
    stage: str | None = None
    course: str | None = None
    group: str | None = None
    day: int | None = None
    level: int | None = 0