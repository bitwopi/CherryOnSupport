import re
from aiogram.filters import Filter
from aiogram import types

    
class TicketFilter(Filter):
    async def __call__(self, query: types.CallbackQuery) -> bool:
        return bool(re.match(r"ticket(_accept|_close):[0-9]+", query.data))

class TicketDenyFilter(Filter):
    async def __call__(self, query: types.CallbackQuery) -> bool:
        return bool(re.match(r"ticket_deny:[0-9]+", query.data))