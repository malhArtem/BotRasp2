from datetime import datetime, time, timedelta
from aiogram import types, Router
from cashews import cache
from aiogram.filters import Command

from parse.parse_shedule import get_parsed_shedule
from parse.shedule_manager import SheduleManager
import bot.keyboard as keyboard
from database import db

router = Router()
cache.setup("mem://") # используем память

@cache(ttl="10m", key="shedules:{user_id}")
async def get_user_shedule(user_id: int, database: db.DataBase) -> SheduleManager:
    parsed = await get_parsed_shedule(user_id, database)
    return SheduleManager(parsed)

# TODO расписание произвольного дня в году

@router.message(Command('today'))
async def show_today(message: types.Message, database: db.DataBase):
    manager = await get_user_shedule(message.from_user.id, database)
    manager.day = datetime.combine(datetime.today(), time(0, 0))
    answer = manager.get_shedule()

    await message.delete()
    await message.answer(answer, reply_markup=keyboard.leaf_buttons().as_markup())

@router.message(Command('week'))
async def show_today(message: types.Message, database: db.DataBase):
    manager = await get_user_shedule(message.from_user.id, database)
    manager.day = datetime.combine(datetime.today(), time(0, 0))
    answer = manager.get_week_shedule()

    await message.delete()
    await message.answer(answer, reply_markup=keyboard.leaf_week_buttons().as_markup())

@router.callback_query(keyboard.to_date_callback.filter())
async def switch_to_date(
    callback_query: types.CallbackQuery,
    callback_data: keyboard.to_date_callback,
    database: db.DataBase
):
    manager = await get_user_shedule(callback_query.from_user.id, database)
    manager.day = datetime.strptime(callback_data.date, "%d-%m-%Y")
    answer = manager.get_shedule()

    await callback_query.answer()
    await callback_query.message.edit_text(
        answer, reply_markup=keyboard.leaf_buttons().as_markup()
    )

@router.callback_query(keyboard.to_week_callback.filter())
async def switch_to_week(
    callback_query: types.CallbackQuery,
    callback_data: keyboard.to_week_callback,
    database: db.DataBase
):
    manager = await get_user_shedule(callback_query.from_user.id, database)
    manager.day = datetime.strptime(callback_data.date, "%d-%m-%Y")
    answer = manager.get_week_shedule()

    await callback_query.answer()
    await callback_query.message.edit_text(
        answer, reply_markup=keyboard.leaf_week_buttons().as_markup()
    )
    
@router.callback_query(keyboard.days_callback.filter())
async def switch_day(
    callback_query: types.CallbackQuery,
    callback_data: keyboard.days_callback,
    database: db.DataBase
):
    manager = await get_user_shedule(callback_query.from_user.id, database)
    manager.day += timedelta(callback_data.move)
    answer = manager.get_shedule()

    await callback_query.answer()
    await callback_query.message.edit_text(
        answer, reply_markup=keyboard.leaf_buttons().as_markup()
    )

@router.callback_query(keyboard.week_callback.filter())
async def switch_week(
    callback_query: types.CallbackQuery,
    callback_data: keyboard.week_callback,
    database: db.DataBase
):
    manager = await get_user_shedule(callback_query.from_user.id, database)
    manager.day += timedelta(7 * callback_data.move)
    answer = manager.get_week_shedule()

    await callback_query.answer()
    await callback_query.message.edit_text(
        answer, reply_markup=keyboard.leaf_week_buttons().as_markup()
    )
