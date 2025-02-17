import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.commands import set_commands
from config import TOKEN, admins_id
from db import DB
from bot.handlers.registration import router as reg_router


properties = DefaultBotProperties(parse_mode="html")


bot = Bot(TOKEN, default=properties)
dp = Dispatcher()
dp.include_router(reg_router)

logger = logging.getLogger(__name__)


async def main():
    await bot.set_webhook('', drop_pending_updates=True)

    db = DB("rasp")
    await set_commands(bot)
    await bot.send_message(admins_id, "Бот запущен")
    await dp.start_polling(bot, db=db)




if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    asyncio.run(main())