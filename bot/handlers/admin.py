from aiogram import types, F
from aiogram import filters
from aiogram.dispatcher.router import Router
from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext

from bot.db import get_ticket_by_id, update_ticket_status, get_user, update_ticket_admin
from bot.filters.admin import TicketFilter
from bot.filters.user import IsAdmin
from bot.keyboards import admin as a_keyboard
from bot.states.admin import TicketStatusState

admin_router = Router(name="admin_router")
admin_router.callback_query.filter(IsAdmin())


async def take_ticket(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TicketStatusState.in_process)
    ticket_id = query.data.split(":")[1]
    ticket = await get_ticket_by_id(ticket_id)
    await state.update_data({'user_id': ticket[4]})
    await update_ticket_admin(ticket_id, query.from_user.id)
    await query.message.edit_reply_markup(query.inline_message_id, 
                                          a_keyboard.get_ticket_close_keyboard(ticket_id))


async def close_ticket(query: types.CallbackQuery, state: FSMContext) -> None:
    ticket_id = query.data.split(":")[1]
    ticket = await get_ticket_by_id(ticket_id)
    if ticket[5] == query.from_user.id and not ticket[2]:
        await update_ticket_status(ticket_id, True)
        await state.clear()
        await query.message.delete_reply_markup()
    else:
        await query.answer("Вы пытаетесь закрыть чужую заявку или взять несколько заявок за раз")


async def chat_with_user(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get('user_id')
    await message.bot.send_message(user_id, message.text)





admin_router.callback_query.register(take_ticket, filters.StateFilter(None), TicketFilter())
admin_router.message.register(chat_with_user,TicketStatusState.in_process)
admin_router.callback_query.register(close_ticket, TicketFilter(), TicketStatusState.in_process)
