from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_question_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        # [InlineKeyboardButton(text="Часто задаваемые вопросы", callback_data="faq")],
        [InlineKeyboardButton(text="Связаться с оператором", callback_data="operator")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Отменить", callback_data="cancel")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)