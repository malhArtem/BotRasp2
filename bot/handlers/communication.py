from aiogram import Router, types
from aiogram.filters import Command

from core.config import config

router = Router()

@router.message(Command("links"))
async def connection_cmd(message: types.Message):
    text = config.text.links
    await message.answer(text)
