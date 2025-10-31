from aiogram import types, F
from aiogram import filters
from aiogram.dispatcher.router import Router
from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from bot.db import get_ticket_by_id, update_ticket_status, get_user, update_ticket_admin
from bot.filters.admin import TicketFilter, TicketDenyFilter
from bot.filters.user import IsAdmin
from bot.keyboards import user as u_keyboard
from bot.keyboards import admin as a_keyboard
from bot.states.admin import TicketStatusState
from bot.texts import admin as texts

admin_router = Router(name="admin_router")
admin_router.callback_query.filter(IsAdmin())


async def deny_ticket(query: types.CallbackQuery, state: FSMContext) -> None:
    ticket_id = query.data.split(":")[1]
    ticket = await get_ticket_by_id(ticket_id)
    ticket_done = ticket[2]
    admin_id = ticket[5]
    user_id = ticket[4]
    if not ticket_done and not admin_id is None:
        await query.bot.send_message(user_id, 
                                    texts.ticket_deny + f"\nНомер заявки: {ticket_id}",
                                    reply_markup=u_keyboard.get_question_keyboard())
        user_state = FSMContext(
            storage=state.storage,
            key=StorageKey(
                bot_id=query.bot.id,
                chat_id=user_id,
                user_id=user_id
            )
        )
        await user_state.clear()
        await state.clear()
        await query.message.delete_reply_markup()
    
async def take_ticket(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TicketStatusState.in_process)
    ticket_id = query.data.split(":")[1]
    ticket = await get_ticket_by_id(ticket_id)
    admin_id = ticket[5]
    if str(admin_id) != str(query.from_user.id):  
        await query.answer(text="Вы пытаетесь взять чужой или закрытый тикет")
        return
    await state.update_data({'user_id': ticket[4]})
    await update_ticket_admin(ticket_id, query.from_user.id)
    await query.message.edit_reply_markup(query.inline_message_id, 
                                        a_keyboard.get_ticket_close_keyboard(ticket_id))


async def close_ticket(query: types.CallbackQuery, state: FSMContext) -> None:
    ticket_id = query.data.split(":")[1]
    ticket = await get_ticket_by_id(ticket_id)
    data = await state.get_data()
    user_id = data.get("user_id")
    if ticket[5] == query.from_user.id and not ticket[2]:
        await update_ticket_status(ticket_id, True)
        await query.bot.send_message(user_id, 
                                     texts.ticket_close + f"\nНомер заявки: {ticket_id}",
                                     reply_markup=u_keyboard.get_question_keyboard())
        user_state = FSMContext(
            storage=state.storage,
            key=StorageKey(
                bot_id=query.bot.id,
                chat_id=user_id,
                user_id=user_id
            )
        )
        await user_state.clear()
        await state.clear()
        await query.message.delete_reply_markup()
    else:
        await query.answer(texts.ticket_edit_error)


async def chat_with_user(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get('user_id')
    await message.bot.send_message(user_id, message.text)




admin_router.callback_query.register(deny_ticket, filters.StateFilter(None), TicketDenyFilter())
admin_router.callback_query.register(take_ticket, filters.StateFilter(None), TicketFilter())
admin_router.callback_query.register(close_ticket, TicketFilter(), TicketStatusState.in_process)
admin_router.message.register(chat_with_user, TicketStatusState.in_process)
