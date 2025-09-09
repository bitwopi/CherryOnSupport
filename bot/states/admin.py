from aiogram.fsm.state import StatesGroup, State


class TicketStatusState(StatesGroup):
    in_process = State()