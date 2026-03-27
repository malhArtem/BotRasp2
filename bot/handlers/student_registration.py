from aiogram import Router, types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cashews import cache
from core.config import config
from bot import keyboard

from database import db
from core import models
from parse import utils
from core import errors


router = Router()
cache.setup("mem://") # используем память

@cache(ttl="1m", key="groups:{key}") #cache либа будет использовать 2 аргумент как ключ
async def get_groups(database: db.DataBase, key: str) -> list[models.Group]: 
    async with database.db_cursor(False) as cursor:
        return await db.GroupsBase.get_groups(cursor)

@router.callback_query(keyboard.level_callback.filter())
async def register_year(callback_query: types.CallbackQuery, callback_data: keyboard.level_callback, database: db.DataBase):
    async with database.db_cursor(False) as cursor:
        groups = await db.GroupsBase.get_groups(cursor)
    key_builder = InlineKeyboardBuilder()

    for year in utils.get_years(groups, callback_data.level):
        key_builder.add(
            InlineKeyboardButton(
                text=str(year),
                callback_data=keyboard.year_callback(
                    year=year,
                    level=callback_data.level,
                    cache=str(year) + callback_data.level
                ).pack()
            )
        )
    key_builder.adjust(3)

    await callback_query.message.edit_text(
        text=config.text.select_year,
        reply_markup=key_builder.as_markup()
    )
    await callback_query.answer()

@router.callback_query(keyboard.year_callback.filter())
async def register_group(callback_query: types.CallbackQuery, callback_data: keyboard.year_callback, database: db.DataBase):
    groups = await get_groups(database, callback_data.cache)
    key_builder = InlineKeyboardBuilder()

    for group in groups:
        print(type(group), group)
        key_builder.add(
            InlineKeyboardButton(
                text=group.code,
                callback_data=keyboard.student_register_callback(group_id=group.group_id).pack()
            )
        )

    await callback_query.message.edit_text(
        text=config.text.select_group,
        reply_markup=key_builder.as_markup()
    )
    await callback_query.answer()

@router.callback_query(keyboard.student_register_callback.filter())
async def student_end_registration(
    callback_query: types.CallbackQuery,
    callback_data: keyboard.student_register_callback,
    database: db.DataBase
):  
    user = callback_query.from_user
    user_profile = models.UserProfile(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        group_id=callback_data.group_id
    )
    print(user_profile)
    async with database.db_cursor() as cursor:
        await db.UsersBase.create_profile(cursor, user_profile)

    await callback_query.message.edit_text(
        text=config.text.done_register
    )
    await callback_query.answer()
