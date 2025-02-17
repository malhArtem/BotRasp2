from aiogram import Bot
from aiogram.types import BotCommand


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='register',
            description='регистрация/смена группы'
        ),
        BotCommand(
            command='today',
            description='расписание на сегодня'
        ),
        BotCommand(
            command='next_day',
            description='расписание на следующий день'
        ),
        BotCommand(
            command='week',
            description='расписание на эту неделю'
        ),
        BotCommand(
            command='next_week',
            description='расписание на следующую неделю'
        ),
        BotCommand(
            command='day',
            description='расписание на любой день'
        ),
        BotCommand(
            command='communication',
            description='связь'
        )
    ]

    await bot.set_my_commands(commands)