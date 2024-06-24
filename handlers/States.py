from aiogram.fsm.state import StatesGroup,State

class States(StatesGroup):
    stage = State()
    course = State()
    group = State()
    day = State()