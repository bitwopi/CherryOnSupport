import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

import config
from bot.handlers.admin import admin_router
from bot.handlers.user import user_router

logger = logging.getLogger(__name__)


def register_all_handlers(dp: Dispatcher) -> None:
    dp.include_routers(user_router)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    storage = MemoryStorage()
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=storage)

    register_all_handlers(dp)

    # start
    try:
        await bot.delete_webhook()
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()
        await dp.shutdown()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")