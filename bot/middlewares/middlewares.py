from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.rdb import RedisDB


class RedisMiddleware(BaseMiddleware):
    def __init__(self, rdb: RedisDB):
        self.rdb = rdb
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data["rdb"] = self.rdb
        return await handler(event, data)