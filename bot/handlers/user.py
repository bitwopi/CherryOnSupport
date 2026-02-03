from aiogram import types, F
from aiogram import filters
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandObject

from bot.rdb import RedisDB
import config
from bot.db import add_ticket, get_last_user_ticket
from bot.keyboards import user as u_keyboard
from bot.keyboards import admin as a_keyboard
from bot.states.user import UserQuestionState
from bot.texts import user as texts

user_router = Router()
user_router.message.filter(F.chat.type == "private")


async def send_start_message(message: types.Message, command: CommandObject, state: FSMContext) -> None:
    await message.delete()
    target = command.args
    if target:
        text = texts.targets.get(target, None)
        if text:
            await forward_question_to_operator_chat(message, state, target_text=text)
            return
    await message.answer(texts.start_text, reply_markup=u_keyboard.get_question_keyboard())


async def send_operator_start_message(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UserQuestionState.start)
    await query.message.edit_text(texts.operator_start, reply_markup=u_keyboard.get_cancel_keyboard())


async def send_cancel_message(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.message.edit_text(texts.start_text, reply_markup=u_keyboard.get_question_keyboard())
    
async def send_cancel_message_com(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.delete()
    await message.answer(texts.start_text, reply_markup=u_keyboard.get_question_keyboard())


async def forward_question_to_operator_chat(message: types.Message, state: FSMContext, rdb: RedisDB, **kwargs) -> None:
    try:
        await add_ticket(content=message.text, user_id=message.from_user.id)
        ticket = await get_last_user_ticket(message.from_user.id)
        ticket_id = ticket[0]
        text = message.text
        target_text = kwargs.get("target_text", None)
        if target_text:
            text = target_text
        for admin in config.ADMIN_LIST.split(","):
            adm_msg = await message.bot.send_message(admin,
                                        text + f"\n\nt.me/{message.from_user.username}\nНомер заявки: {ticket_id}",
                                        reply_markup=a_keyboard.get_ticket_keyboard(ticket_id))
            rdb.add_ticket_messageid(ticket_id, admin, adm_msg.message_id)
        await message.answer("Оператор скоро с вами свяжется")
        await state.set_state(UserQuestionState.waiting_for_operator)
    except Exception as e:
        print(config.ADMIN_CHAT_ID)
        print(e)
        await message.answer(texts.wrong_msg)
        

async def check_for_operator(message: types.Message, state: FSMContext) -> None: 
    ticket = await get_last_user_ticket(message.from_user.id)
    if ticket[5] and not ticket[2]:
        await state.set_state(UserQuestionState.in_process)
        await state.update_data({'admin_id': ticket[5]})
        await chat_with_operator(message, state)
    else:
        await message.answer("К вам пока не приставлен оператор, пожалуйста подождите")
     
     
async def check_ticket_status(user_id) -> bool:
    ticket = await get_last_user_ticket(user_id)
    return ticket[2]
    
async def chat_with_operator(message: types.Message, state: FSMContext) -> None:
    if await check_ticket_status(message.from_user.id):
        await message.answer("Ваше обращение закрыто администратором")
        await state.clear()
        return
    
    data = await state.get_data()
    admin_id = data['admin_id']
    if message.text:
        await message.bot.send_message(admin_id, message.text)
    elif message.photo:
        await message.bot.send_photo(admin_id, message.photo[-1].file_id)
    elif message.video:
        await message.bot.send_video(admin_id, message.video.file_id)
    elif message.document:
        await message.bot.send_document(admin_id, message.document.file_id)


async def send_wrong_type_message(message: types.Message) -> None:
    await message.answer("Я понимаю только текст, пожалуйста общайтесь со мной буквами 🤖")


async def send_warn_message(message: types.Message) -> None:
    await message.answer("Я не понимаю, что вы говорите, пожалуйста используйте команды или кнопки 🤖")


user_router.message.register(send_start_message, filters.CommandStart())
user_router.message.register(forward_question_to_operator_chat, UserQuestionState.start)
user_router.callback_query.register(send_operator_start_message, F.data == "operator")
user_router.callback_query.register(send_cancel_message, F.data == "cancel")
user_router.message.register(send_cancel_message_com, filters.Command("cancel"))
user_router.message.register(check_for_operator, UserQuestionState.waiting_for_operator)
user_router.message.register(chat_with_operator, UserQuestionState.in_process)
user_router.message.register(send_wrong_type_message, ~F.text)
