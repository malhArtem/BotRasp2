from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from core.config import config

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command=key, description=value)
        for key, value in config.commands.items()
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())