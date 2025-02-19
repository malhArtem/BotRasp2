import calendar
import datetime

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboard import cb_days, cb_month, cb_day, leaf_kb
from db import DB
from get_raspisanie import student_rasp, get_teach_rasp

router = Router()

async def day_rasp(user, message, day, db):
    if not user[2]:
        text = await student_rasp(message, day, db)  # формируем сообщение
    else:
        text = await get_teach_rasp(day, message, db)
    return text


@router.message(Command("today"))
async def today_rasp(message: types.Message, db: DB):
    user = await db.get_user(message.from_user.id)  # получаем данные пользователя (курс, группу)
    ikb = InlineKeyboardBuilder()
    if user is not None:
        today = datetime.datetime.now()  # получаем дату на момент написания сообщения
        text = await day_rasp(user, message, today, db)

        ikb = leaf_kb(ikb, today)

    else:
        text = "Вы не зарегистрированы"
        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
    await message.answer(text, reply_markup=ikb.as_markup())  # отправляем сообщение


@router.message(Command("next_day"))
async def next_day_rasp(message: types.Message, db: DB):
    user = await db.get_user(message.from_user.id)
    ikb = InlineKeyboardBuilder()
    if user is not None:
        day = datetime.datetime.now() + datetime.timedelta(days=1)
        if day.weekday() == 6:
            day = day + datetime.timedelta(days=1)
        text = await day_rasp(user, message, day, db)
        ikb = leaf_kb(ikb, day)

    else:
        text = "Вы не зарегистрированы"
        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
    await message.answer(text, reply_markup=ikb.as_markup())


@router.message(Command("week"))
async def week_rasp(message: types.Message, db):
    user = await db.get_user(message.from_user.id)
    ikb = InlineKeyboardBuilder()
    if user is not None:
        day = datetime.datetime.now()
        week_day = day.weekday()
        day = day - datetime.timedelta(days=week_day)
        for i in range(6):
            text = await day_rasp(user, message, day, db)
            await message.answer(text)
            day = day + datetime.timedelta(days=1)

    else:
        text = "Вы не зарегистрированы"
        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
        await message.answer(text, parse_mode='html', reply_markup=ikb.as_markup())


@router.message(Command("next_week"))
async def week_rasp(message: types.Message, db):
    ikb = InlineKeyboardBuilder()
    user = await db.get_user(message.from_user.id)
    if user is not None:
        day = datetime.datetime.now()
        week_day = day.weekday()
        day = day - datetime.timedelta(days=week_day) + datetime.timedelta(days=7)

        for i in range(1, 6):
            text = await day_rasp(user, message, day, db)
            await message.answer(text)
            day = day + datetime.timedelta(days=1)
    else:
        text = "Вы не зарегистрированы"
        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
        await message.answer(text, parse_mode='html', reply_markup=ikb.as_markup())


@router.callback_query(F.data=="choose_month")
@router.message(Command('day'))
async def choose_month(message: types.Message, db: DB):
    user = await db.get_user(message.from_user.id)
    i_kb = InlineKeyboardBuilder()
    if user is not None:
        today = datetime.datetime.now()
        month = today.month
        text = "Выберите месяц"
        if  month < 9:
            for i in range(month, 9):
                ib = InlineKeyboardButton(text=str(i), callback_data=cb_month(month=i).pack())
                i_kb.add(ib)
        else:
            for i in range(month, 13):
                ib = InlineKeyboardButton(text=str(i), callback_data=cb_month(month=i).pack())
                i_kb.add(ib)
        i_kb.adjust(3)
    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="Зарегистрироваться", callback_data="register")
        i_kb.row(ib)
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=i_kb.as_markup())
    else:
        await message.answer()
        await message.message.edit_text(text, reply_markup=i_kb.as_markup())



@router.callback_query(cb_month.filter())
async def choose_day(callback_query: types.CallbackQuery, callback_data: cb_month):
    today = datetime.datetime.now()
    i_kb = InlineKeyboardBuilder()
    year = today.year
    month = calendar.monthrange(year, callback_data.month)
    for i in range(1, month[1]+1):
        ib = InlineKeyboardButton(text=str(i), callback_data=cb_days(
            date=datetime.date(today.year, callback_data.month, i).strftime('%d.%m.%Y')).pack())
        i_kb.add(ib)
    i_kb.adjust(7)
    ib = InlineKeyboardButton(text="👈", callback_data="choose_month")
    i_kb.row(ib)
    await callback_query.answer()
    await callback_query.message.edit_text("Выберите день:", reply_markup=i_kb.as_markup())



@router.callback_query(cb_days.filter())
async def date_rasp(callback_query: types.CallbackQuery, callback_data: cb_days, db: DB):
    date = datetime.datetime.strptime(callback_data.date, '%d.%m.%Y')
    user = await db.get_user(callback_query.from_user.id)

    if not user[2]:
        text = await student_rasp(callback_query, date, db)
    else:
        text = await get_teach_rasp(date, callback_query, db)

    ikb = InlineKeyboardBuilder()
    ikb = leaf_kb(ikb, date)
    await callback_query.answer()
    await callback_query.message.edit_text(text=text, reply_markup=ikb.as_markup())
