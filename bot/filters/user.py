from aiogram.filters import Filter
from aiogram.types import Message

from bot.db import get_user, is_in_blacklist, is_admin

class IsRegistered(Filter):

    async def __call__(self, message: Message):
        user = await get_user(message.from_user.id)
        return user is not None or len(user) > 0


class IsInBlacklist(Filter):

    async def __call__(self, message: Message):
        return await is_in_blacklist(message.from_user.id)


class IsAdmin(Filter):

    async def __call__(self, message: Message):
        return await is_admin(message.from_user.id)