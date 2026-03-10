import calendar
import datetime

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cashews import cache

from core import errors
from parse.parse_shedule import get_parsed_shedule
from shedule_manager import SheduleManager
from bot.keyboard import cb_month, days_callback, leaf_buttons, to_date_callback, register_callback
from database import db

router = Router()
cache.setup("mem://") # используем память

@cache(ttl="10m", key="shedules:{user_id}")
async def get_user_shedule(user_id: int, database: db.DataBase) -> SheduleManager:
    parsed = await get_parsed_shedule(user_id, database)
    return SheduleManager(parsed)


@router.message(Command("today"))
async def today_shedule(message: types.Message, database: db.DataBase):
    await message.delete()
    key_builder = InlineKeyboardBuilder()
    try:
        manager = await get_user_shedule(message.from_user.id, database)
        answer = manager.get_shedule()
        key_builder = leaf_buttons(key_builder)

    except errors.UserNotFoundError:
        answer = "Вы не зарегистрированы"
        key_builder.add(
            InlineKeyboardButton(text="3арегистрироваться", callback_data=register_callback().pack())
        )

    await message.answer(answer, reply_markup=key_builder.as_markup())


@router.message(Command("next_day"))
async def next_day_rasp(message: types.Message, database: db.DataBase):
    await message.delete()
    key_builder = InlineKeyboardBuilder()
    try:
        manager = await get_user_shedule(message.from_user.id, database)
        answer = manager.next_shedule()
        key_builder = leaf_buttons(key_builder)

    except errors.UserNotFoundError:
        answer = "Вы не зарегистрированы"
        key_builder.add(
            InlineKeyboardButton(text="3арегистрироваться", callback_data=register_callback().pack())
        )

    await message.answer(answer, reply_markup=key_builder.as_markup())


@router.message(Command("week"))
async def week_rasp(message: types.Message, database: db.DataBase):
    await message.delete()
    key_builder = InlineKeyboardBuilder()
    try:
        manager = await get_user_shedule(message.from_user.id, database)
        tmp_day = datetime.datetime.combine(
            datetime.datetime.today(),
            datetime.time(0, 0)
        ) - datetime.timedelta(days=datetime.datetime.today().weekday())

        for _ in range(6):
            await message.answer(
                manager.get_shedule(tmp_day)
            )
            tmp_day += datetime.timedelta(days=1)

    except errors.UserNotFoundError:
        key_builder.add(
            InlineKeyboardButton(text="Зарегистрироваться", callback_data=register_callback().pack())
        )
        await message.answer("Вы не зарегистрированы", reply_markup=key_builder.as_markup())


@router.message(Command("next_week"))
async def week_rasp(message: types.Message, database: db.DataBase):
    await message.delete()
    key_builder = InlineKeyboardBuilder()
    try:
        manager = await get_user_shedule(message.from_user.id, database)
        tmp_day = datetime.datetime.combine(
            datetime.datetime.today(),
            datetime.time(0, 0)
        ) - datetime.timedelta(
            days=datetime.datetime.today().weekday
        ) + datetime.timedelta(days=7)

        for _ in range(6):
            await message.answer(
                manager.get_shedule(tmp_day)
            )
            tmp_day += datetime.timedelta(days=1)

    except errors.UserNotFoundError:
        key_builder.add(
            InlineKeyboardButton(text="3арегистрироваться", callback_data=register_callback().pack())
        )
        await message.answer("Вы не зарегистрированы", reply_markup=key_builder.as_markup())


@router.callback_query(F.data=="choose_month")
@router.message(Command('day'))
async def choose_month(message: types.Message, database: db.DataBase):
    try:
        await get_user_shedule(message.from_user.id, database)

        key_builder = InlineKeyboardBuilder()
        month = datetime.datetime.today().month
        answer = "Выберите месяц"

        if month < 9:
            for i in range(month, 9):
                key_builder.add(
                    InlineKeyboardButton(text=str(i), callback_data=cb_month(month=i).pack())
                )
        else:
            for i in range(month, 13):
                key_builder.add(
                    InlineKeyboardButton(text=str(i), callback_data=cb_month(month=i).pack())
                )

        key_builder.adjust(3)

    except errors.UserNotFoundError:
        answer = "Вы не зарегистрированы"
        key_builder.row(
            InlineKeyboardButton(text="Зарегистрироваться", callback_data=register_callback().pack())
        )
        
    if isinstance(message, types.Message):
        await message.answer(answer, reply_markup=key_builder.as_markup())
    else:
        await message.answer()
        await message.message.edit_text(answer, reply_markup=key_builder.as_markup())


@router.callback_query(cb_month.filter())
async def choose_day(callback_query: types.CallbackQuery, callback_data: cb_month):
    key_builder = InlineKeyboardBuilder()

    year = datetime.datetime.today().year
    month = calendar.monthrange(year, callback_data.month)

    for i in range(1, month[1]+1):
        day_button = InlineKeyboardButton(text=str(i), callback_data=to_date_callback(
            date=datetime.datetime(year, callback_data.month, i)).pack()
        )
        key_builder.add(day_button)

    key_builder.adjust(7)
    key_builder.row(
        InlineKeyboardButton(text="👈", callback_data="choose_month")
    )

    await callback_query.answer()
    await callback_query.message.edit_text("Выберите день:", reply_markup=key_builder.as_markup())


@router.callback_query(to_date_callback.filter())
async def switch_to_date(callback_query: types.CallbackQuery, callback_data: to_date_callback, database: db.DataBase):
    manager = await get_user_shedule(callback_query.from_user.id, database)
    answer = manager.get_shedule(datetime.datetime.strptime(callback_data.date, "%d-%m-%Y"))

    key_builder = leaf_buttons(InlineKeyboardBuilder())
    await callback_query.answer()
    await callback_query.message.edit_text(text=answer, reply_markup=key_builder.as_markup())


@router.callback_query(days_callback.filter())
async def date_rasp(callback: types.CallbackQuery, callback_data: days_callback, database: db.DataBase):
    manager = await get_user_shedule(callback.from_user.id, database)

    if callback_data.move == -1:
        answer = manager.prev_shedule()
    else:
        answer = manager.next_shedule()

    key_builder = leaf_buttons(InlineKeyboardBuilder())
    await callback.message.edit_text(text=answer, reply_markup=key_builder.as_markup())
