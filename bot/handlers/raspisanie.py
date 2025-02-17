import datetime

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import DB

router = Router()


@router.message(Command("today"))
async def today_rasp(message: types.Message, db: DB):
    user = await db.get_user(message.from_user.id)  # получаем данные пользователя (курс, группу)
    ikb = InlineKeyboardBuilder()
    if user is not None:
        today = datetime.datetime.now()  # получаем дату на момент написания сообщения
        if user[2] == 0:
            text = await day_rasp(message, today)  # формируем сообщение
        else:
            text = await db.get_teach_rasp(today, message)

        ib1 = InlineKeyboardButton(text="👈", callback_data=cb_days.new(
            date=(today - datetime.timedelta(days=1)).strftime('%d.%m.%Y')))

        ib2 = InlineKeyboardButton(text="👉", callback_data=cb_days.new(
            date=(today + datetime.timedelta(days=1)).strftime('%d.%m.%Y')))

        ikb.row(ib1, ib2)
    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
    await message.answer(text,
                         # parse_mode='html',
                         reply_markup=ikb)  # отправляем сообщение


@dp.message_handler(commands=["next_day"])
async def next_day_rasp(message: types.Message):
    user = await get_user(message.from_user.id)
    ikb = InlineKeyboardMarkup()
    if user is not None:
        day = datetime.datetime.now() + datetime.timedelta(days=1)
        if day.weekday() == 6:
            day = day + datetime.timedelta(days=1)
        if user[2] == 0:
            text = await day_rasp(message, day)

        else:
            text = await get_teach_rasp(day, message)

        ib1 = InlineKeyboardButton(text="👈", callback_data=cb_days.new(
            date=(day - datetime.timedelta(days=1)).strftime('%d.%m.%Y')))

        ib2 = InlineKeyboardButton(text="👉", callback_data=cb_days.new(
            date=(day + datetime.timedelta(days=1)).strftime('%d.%m.%Y')))

        ikb.row(ib1, ib2)

    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
    await message.answer(text, parse_mode='html', reply_markup=ikb)


@dp.message_handler(commands=["week"])
async def week_rasp(message: types.Message):
    user = await get_user(message.from_user.id)
    ikb = InlineKeyboardMarkup()
    if user is not None:
        day = datetime.datetime.now()
        week_day = day.weekday()

        day = day - datetime.timedelta(days=week_day)

        if user[2] == 0:
            text = await day_rasp(message, day)
        else:
            text = await get_teach_rasp(day, message)

        await message.answer(text, parse_mode='html')

        for i in range(1, 6):
            day = day + datetime.timedelta(days=1)
            if user[2] == 0:
                text = await day_rasp(message, day)
            else:
                text = await get_teach_rasp(day, message)

            await message.answer(text, parse_mode='html')

    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
        await message.answer(text, parse_mode='html', reply_markup=ikb)


@dp.message_handler(commands=["next_week"])
async def week_rasp(message: types.Message):
    ikb = InlineKeyboardMarkup()
    user = await get_user(message.from_user.id)
    if user is not None:
        day = datetime.datetime.now()
        week_day = day.weekday()

        day = day - datetime.timedelta(days=week_day) + datetime.timedelta(days=7)
        if user[2] == 0:
            text = await day_rasp(message, day)
        else:
            text = await get_teach_rasp(day, message)
        await message.answer(text, parse_mode='html')

        for i in range(1, 6):
            day = day + datetime.timedelta(days=1)
            if user[2] == 0:
                text = await day_rasp(message, day)
            else:
                text = await get_teach_rasp(day, message)

            await message.answer(text, parse_mode='html')
    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
        await message.answer(text, parse_mode='html', reply_markup=ikb)


@dp.callback_query_handler(text="choose_month")
@dp.message_handler(commands=['day'])
async def choose_month(message: types.Message):
    user = await get_user(message.from_user.id)
    i_kb = InlineKeyboardMarkup(row_width=3)
    if user is not None:
        today = datetime.datetime.now()
        str_month = today.strftime("%Y-%m-%d").split('-')[1]
        text = "Выберите месяц"
        if int(str_month) < 9:
            for i in range(int(str_month), 9):
                ib = InlineKeyboardButton(str(i), callback_data=cb_month.new(number=str(i)))
                i_kb.insert(ib)
        else:
            for i in range(int(str_month), 13):
                ib = InlineKeyboardButton(str(i), callback_data=cb_month.new(number=str(i)))
                i_kb.insert(ib)

    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="Зарегистрироваться", callback_data="register")
        i_kb.add(ib)
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=i_kb)
    else:
        await bot.answer_callback_query(message.id)
        await message.message.edit_text(text, reply_markup=i_kb)



@dp.callback_query_handler(cb_month.filter())
async def choose_day(callback_query: types.CallbackQuery, callback_data: dict):
    today = datetime.datetime.now()
    i_kb = InlineKeyboardMarkup(row_width=7)
    str_year = today.strftime("%Y-%m-%d").split('-')[0]
    month = calendar.monthrange(int(str_year), int(callback_data.get('number')))
    for i in range(0, month[1]):
        ib = InlineKeyboardButton(str(i + 1), callback_data=cb_day.new(month=callback_data.get('number'),
                                                                       number=str(i + 1)))
        i_kb.insert(ib)
    ib = InlineKeyboardButton("👈", callback_data="choose_month")
    i_kb.insert(ib)
    await bot.answer_callback_query(callback_query.id)
    # await callback_query.message.delete()
    await callback_query.message.edit_text("Выберите день:", reply_markup=i_kb)


@dp.callback_query_handler(cb_day.filter())
async def date_rasp(callback_query: types.CallbackQuery, callback_data: dict):
    today = datetime.datetime.now()
    user = await get_user(callback_query.from_user.id)

    str_year = today.strftime("%Y-%m-%d").split('-')[0]
    str_date = str_year + '-' + callback_data.get('month') + '-' + callback_data.get('number')
    date = datetime.datetime.strptime(str_date, "%Y-%m-%d")
    if user[2] == 0:
        text = await day_rasp(callback_query, date)
    else:
        text = await get_teach_rasp(date, callback_query)

    ikb = InlineKeyboardMarkup()

    ib1 = InlineKeyboardButton(text="👈", callback_data=cb_days.new(
        date=(date - datetime.timedelta(days=1)).strftime('%d.%m.%Y')))

    ib2 = InlineKeyboardButton(text="👉", callback_data=cb_days.new(
        date=(date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')))

    ikb.row(ib1, ib2)

    await bot.answer_callback_query(callback_query.id)
    # await callback_query.message.delete()
    await callback_query.message.edit_text(text=text,reply_markup=ikb, parse_mode='html')


@dp.callback_query_handler(cb_days.filter())
async def date_rasp(callback_query: types.CallbackQuery, callback_data: dict):
    date = datetime.datetime.strptime(callback_data.get('date'), '%d.%m.%Y')
    user = await get_user(callback_query.from_user.id)

    if user[2] == 0:
        text = await day_rasp(callback_query, date)
    else:
        text = await get_teach_rasp(date, callback_query)

    ikb = InlineKeyboardMarkup()

    ib1 = InlineKeyboardButton(text="👈", callback_data=cb_days.new(
        date=(date - datetime.timedelta(days=1)).strftime('%d.%m.%Y')))

    ib2 = InlineKeyboardButton(text="👉", callback_data=cb_days.new(
        date=(date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')))

    ikb.row(ib1, ib2)
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text(text=text, reply_markup=ikb, parse_mode='html')
