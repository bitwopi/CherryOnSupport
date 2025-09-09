from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_ticket_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Взять", callback_data=f"ticket_accept:{ticket_id}")],
        [InlineKeyboardButton(text="Отклонить", callback_data=f"ticket_deny:{ticket_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_ticket_close_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Закрыть", callback_data=f"ticket_close:{ticket_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)