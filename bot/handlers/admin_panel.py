from aiogram import Router, types, F
from aiogram.filters import Command
from core.config import config
import bot.admin_keyboard as keyboard

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import database.db as db
from core import models as models

class NewGroup(StatesGroup):
    info = State()

router = Router()

@router.message(Command('admin'))
async def admin_panel(message: types.Message):
    if message.from_user.id not in config.administration.admins: return
    
    await message.delete()
    await message.answer(
        text=config.text.admin_title, reply_markup=keyboard.admin_panel().as_markup()
    )

@router.callback_query(keyboard.add_group_callback.filter())
async def add_group(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=config.text.admin_add_group
    )
    await state.update_data(parent_message_id=callback.message.message_id)
    await state.set_state(NewGroup.info)

@router.message(NewGroup.info)
async def process_add_group(message: types.Message, state: FSMContext, database: db.DataBase):
    state_data = await state.get_data()
    parent_message_id = state_data.get("parent_message_id")
    group_data = message.text.split()

    await message.delete()
    if len(group_data) != 3:
        await message.bot.edit_message_text(
            text=config.text.invalid_data,
            chat_id=message.chat.id,
            message_id=parent_message_id
        )
        await state.set_state(NewGroup.code)
        return
    
    group = models.Group(
        level=group_data[0],
        year=group_data[1],
        code=group_data[2]
    )

    async with database.db_cursor() as cursor:
        await db.GroupsBase.create_group(cursor, group)

    await message.bot.edit_message_text(
        text=config.text.success_operation,
        reply_markup=keyboard.admin_panel().as_markup(),
        chat_id=message.chat.id,
        message_id=parent_message_id
    )