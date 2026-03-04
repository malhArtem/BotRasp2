import asyncio
import logging
import importlib
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.commands import set_commands
from core.config import settings
import database.db as db

properties = DefaultBotProperties(parse_mode="html")
logger = logging.getLogger(__name__)

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

def load_routers(dp: Dispatcher):
    files = os.listdir("bot/handlers")

    for file in files:
        if file.endswith(".py"):
            try:
                router_file = importlib.import_module(f"bot.handlers.{file[:-3]}")
            except Exception as e:
                logger.error(f"[X] Error with loading router {file}:\n > {e}")
                continue

            if hasattr(router_file, "router"):
                router = getattr(router_file, "router")
                dp.include_router(router)
                logger.info(f"[O] Router {file} loaded")

            else:
                logger.warning(f"[!] File {file} its not a router!")
            
bot = Bot(settings.TOKEN, default=properties)
dp = Dispatcher()
load_routers(dp)

async def main():
    database = db.DataBase("base.db")
    await db.create_tables(database)
    await set_commands(bot)

    await bot.set_webhook('', drop_pending_updates=True)
    await bot.send_message(settings.ADMIN_ID, "Бот запущен")
    await dp.start_polling(bot, database=database)

if __name__ == "__main__":
    logger.info("Starting bot")
    asyncio.run(main())