import asyncio

from aiogram import types
from core.config import config
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import keyboard

def delete_after(message: types.Message, ttl: int):
    '''
    Delete message after ttl seconds
    Args:
        message: aiogram.types.Message
        ttl: time before delete, in seconds
    '''
    async def wrapper(message: types.Message, ttl: int):
        await asyncio.sleep(ttl)
        await message.delete()
    
    _ = asyncio.create_task(wrapper(message, ttl))

async def show_register(message: types.Message, edit: bool = False) -> None:
    '''
    Shows registration panel and delete it after 24 hours
    Args:
        message: aiogram.types.Message
        edit: edit message or send new
    '''
    register_message = config.text.new_user
    key_builder = InlineKeyboardBuilder()

    for level in config.database.study_levels:
        key_builder.add(
            types.InlineKeyboardButton(text=level, callback_data=keyboard.level_callback(level=level).pack())
        )
    key_builder.add(
        types.InlineKeyboardButton(text="Преподаватель", callback_data=keyboard.im_teacher_callback().pack())
    )
    key_builder.adjust(1)

    if edit:
        await message.edit_text(
            text=register_message,
            reply_markup=key_builder.as_markup()
        )
    else:
        answer = await message.answer(
            text=register_message,
            reply_markup=key_builder.as_markup()
        )
        delete_after(answer, 10)#60 * 60 * 24) # телеграм не разрешает редактирование сообщений старше 48 часов, поэтому удалим пораньше