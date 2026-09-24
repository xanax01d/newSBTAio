from aiogram.filters.callback_data import CallbackData


class MenuCB(CallbackData, prefix="menu"):
    """Navigation callback for stage -> course -> group -> day -> schedule."""

    level: int
    stage: str = ""
    course: int = 0
    group: str = ""
    day: int = 0
    week: int = 0


class QuickCB(CallbackData, prefix="quick"):
    """Quick schedule access for user's saved group."""

    action: str  # "today", "tomorrow", "week", "change_group"


class ReportCB(CallbackData, prefix="rep"):
    """Report & captcha flow callbacks."""

    action: str  # "start", "verify"
    stage: str = ""
    course: int = 0
    group: str = ""
    day: int = 0
    captcha: str = ""
