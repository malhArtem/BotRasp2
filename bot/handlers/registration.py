from aiogram import Router, types
from aiogram.filters import Command

from core.config import config
from bot import keyboard

from database import db
from bot import tools

router = Router()

@router.message(Command('start', 'register'))
async def register_handler(message: types.Message, database: db.DataBase):
    async with database.db_cursor(False) as cursor:
        await db.UsersBase.get_profile(cursor, message.from_user.id)

    await message.delete()
    await message.answer(
        config.text.already_register,
        reply_markup=keyboard.student_menu().as_markup()
    )

@router.callback_query(keyboard.register_callback.filter())
async def register_callback(callback: types.CallbackQuery):
    await tools.show_register(callback.message, True)
    await callback.answer()