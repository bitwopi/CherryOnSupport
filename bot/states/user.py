from aiogram.fsm.state import State, StatesGroup


class UserQuestionState(StatesGroup):
    start = State()
    waiting_for_operator = State()
    in_process = State()