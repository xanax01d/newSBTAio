from aiogram.fsm.state import State, StatesGroup


class MenuStates(StatesGroup):
    """FSM states for schedule navigation."""

    stage = State()
    course = State()
    group = State()
    day = State()
    schedule = State()


class ReportStates(StatesGroup):
    """FSM states for error reporting with captcha."""

    captcha = State()
    sent = State()
