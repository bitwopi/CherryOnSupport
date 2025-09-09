from aiogram import types, F
from aiogram import filters
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramMigrateToChat, TelegramBadRequest

import config
from bot.db import add_ticket, get_last_user_ticket, get_user, get_ticket_by_id
from bot.filters.user import IsRegistered, IsInBlacklist
from bot.keyboards import user as u_keyboard
from bot.keyboards import admin as a_keyboard
from bot.states.user import UserQuestionState
from bot.handlers.admin import admin_router

user_router = Router()
user_router.message.filter(~IsInBlacklist(), F.chat.type == "private")


async def send_start_message(message: types.Message) -> None:
    await message.answer("Привет, я бот поддержки CherryOn!\nЧем я могу тебе помочь?", 
                         reply_markup=u_keyboard.get_question_keyboard())


async def send_operator_start_message(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UserQuestionState.start)
    await query.message.answer(
        "Опишите мне вашу проблему, я отошлю ваше сообщение администратору и он с вами свяжется",
        reply_markup=u_keyboard.get_cancel_keyboard())


async def send_cancel_message(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await send_start_message(message=query.message)


async def forward_question_to_operator_chat(message: types.Message, state: FSMContext) -> None:
    try:
        await add_ticket(content=message.text, user_id=message.from_user.id)
        ticket = await get_last_user_ticket(message.from_user.id)
        ticket_id = ticket[0]
        await message.bot.send_message(config.ADMIN_CHAT_ID,
                                       message.text + f"\n\nt.me/{message.from_user.username}\nНомер заявки: {ticket_id}",
                                       reply_markup=a_keyboard.get_ticket_keyboard(ticket_id))
        await message.answer("Оператор скоро с вами свяжется")
        await state.set_state(UserQuestionState.waiting_for_operator)
    except Exception as e:
        print(config.ADMIN_CHAT_ID)
        print(e)
        await message.answer("🛟Что-то пошло не так, похоже вы попытались отправить в запросе что-то помимо текста.\n"
                             "🔤Пожалуйста опишите вашу проблему текстовым сообщением")
        

async def check_for_operator(message: types.Message, state: FSMContext) -> None: 
    ticket = await get_last_user_ticket(message.from_user.id)
    if ticket[5] and not ticket[2]:
        await state.set_state(UserQuestionState.in_process)
        await state.update_data({'admin_id': ticket[5]})
        await chat_with_operator(message, state)
    else:
        message.answer("К вам пока не приставлен оператор, пожалуйста подождите")
     
    
async def chat_with_operator(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    await message.bot.send_message(data['admin_id'], text=message.text)


async def send_wrong_type_message(message: types.Message) -> None:
    await message.answer("Я понимаю только текст, пожалуйста общайтесь со мной буквами 🤖")


async def send_warn_message(message: types.Message) -> None:
    await message.answer("Я не понимаю, что вы говорите, пожалуйста используйте команды или кнопки 🤖")


user_router.message.register(send_start_message, filters.CommandStart())
user_router.message.register(forward_question_to_operator_chat, UserQuestionState.start)
user_router.callback_query.register(send_operator_start_message, F.data == "operator")
user_router.callback_query.register(send_cancel_message, F.data == "cancel")
user_router.callback_query.register(check_for_operator, UserQuestionState.waiting_for_operator)
user_router.callback_query.register(chat_with_operator, UserQuestionState.in_process)
user_router.message.register(send_wrong_type_message, ~F.text)
user_router.include_routers(admin_router)