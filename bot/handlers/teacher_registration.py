from aiogram import Router, types

from cashews import cache
from core.config import config
from bot import keyboard

import database.db as db
from core import models

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

class SearchTeacher(StatesGroup):
    fio = State()

router = Router()
cache.setup("mem://") # используем память

@cache(ttl="24h", key="teachers")
async def get_groups(database: db.DataBase) -> list[models.Teacher]: 
    async with database.db_cursor(False) as cursor:
        return await db.TeachersBase.get_teachers(cursor)
    
@router.callback_query(keyboard.im_teacher_callback.filter())
async def search_teacher(message: types.Message, state: FSMContext, database: db.DataBase):
    await message.edit_text(
        config.text.input_teacher_fio
    )
    await state.set_state(SearchTeacher.fio)

@router.message(SearchTeacher.fio)
async def register_teacher(): ...