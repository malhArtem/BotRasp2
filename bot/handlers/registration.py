import datetime

from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboard import cb_kurs, cb_pag_teacher, cb_group, cb_teacher, cb_days
from database.db import DB

router = Router()

@router.message(Command('start', 'register'))
@router.callback_query(F.data=="kurs")
@router.callback_query(F.data=="register")
async def user_reg_kurs(message: types.Message, db: DB, bot: Bot):
    builder = InlineKeyboardBuilder() # создание Inline-клавиатуры
    kurses = await db.get_kurs()
    for kurs in kurses:
        if kurs[1] != 'users' and not ('old' in kurs[1]):
            ib = InlineKeyboardButton(text=kurs[1], callback_data=cb_kurs(kurs=kurs[1]).pack())  # создание Inline-кнопки
            builder.add(ib)  # добавление кнопки в клавиатуру
    ib = InlineKeyboardButton(text="Преподаватель", callback_data=cb_pag_teacher(pag=0).pack())
    builder.adjust(2)
    builder.row(ib)
    if isinstance(message, types.Message):
        await message.delete()
        await message.answer(
            "Здравствуй, математик!\nПройди небольшую регистрацию и сможешь наблюдать свое расписание.\nВыбери свой курс:",
            reply_markup=builder.as_markup())
    else:
        await message.message.edit_text(
            text="""Здравствуй, математик!\nПройди небольшую регистрацию и сможешь наблюдать свое расписание.\nВыбери свой курс:""",
            reply_markup=builder.as_markup())
        await bot.answer_callback_query(message.id)


@router.callback_query(cb_kurs.filter())
async def user_reg_group(callback_query: types.CallbackQuery, callback_data: cb_kurs, db: DB, bot: Bot):
    groups = await db.get_groups(callback_data.kurs)
    groups.sort()
    # if callback_data.get('number') == "СПО":
    #     width = 2
    # else:
    #     width = 3
    i_kb_groups = InlineKeyboardBuilder()

    if len(groups) > 1:
        for i in range(len(groups) - 1):
            if groups[i][0] == groups[i + 1][0] or groups[i][0] == groups[i - 1][0]:
                group = f'{groups[i][1]} {groups[i][0]}'
            else:
                group = groups[i][0]

            ib = InlineKeyboardButton(text=group, callback_data=cb_group(kurs=callback_data.kurs, group=group).pack())
            i_kb_groups.add(ib)

        if groups[-1][0] == groups[-2][0]:
            group = f'{groups[-1][1]} {groups[-1][0]}'
        else:
            group = groups[-1][0]

        ib = InlineKeyboardButton(text=group, callback_data=cb_group(kurs=callback_data.kurs, group=group).pack())
        i_kb_groups.add(ib)

    elif groups[0] is not None:
        group = groups[-1][0]
        ib = InlineKeyboardButton(text=group, callback_data=cb_group(kurs=callback_data.kurs, group=group).pack())
        i_kb_groups.add(ib)

    i_kb_groups.adjust(3)

    ib = InlineKeyboardButton(text='👈', callback_data='kurs')
    i_kb_groups.row(ib)
    # await callback_query.message.delete()
    await callback_query.answer()
    try:
        await callback_query.message.edit_text(text="Замечательно! \nВыбери свою группу:", reply_markup=i_kb_groups.as_markup())
    except Exception:
        await callback_query.message.answer(text="Замечательно! \nВыбери свою группу:", reply_markup=i_kb_groups.as_markup())


@router.callback_query(cb_pag_teacher.filter())
async def user_reg_teach(callback_query: types.CallbackQuery, callback_data: cb_pag_teacher, db: DB):
    db.create_table_users()

    i_kb = InlineKeyboardBuilder()
    teachers = await db.get_teachers()
    teachers.sort()

    pag = callback_data.pag

    start = pag * 24
    stop = (pag + 1) * 24 if (pag + 1) * 24 < len(teachers) else len(teachers)
    for i in range(start, stop):
        ib = InlineKeyboardButton(text=str(teachers[i][0]), callback_data=cb_teacher(name=str(teachers[i][0])).pack())
        i_kb.add(ib)
    i_kb.adjust(2)
    spec_buttons = []

    if pag > 0:
        ib = InlineKeyboardButton(text="👈", callback_data=cb_pag_teacher(pag=pag - 1).pack())
        spec_buttons.append(ib)

    ib_back = InlineKeyboardButton(text="Назад", callback_data='kurs')
    spec_buttons.append(ib_back)
    if stop != len(teachers):
        ib = InlineKeyboardButton(text="👉", callback_data=cb_pag_teacher(pag=pag + 1).pack())
        spec_buttons.append(ib)

    i_kb.row(*spec_buttons)

    # db.create_table_users()
    await db.create_profile_teacher(callback_query, '')
    user = list(await db.get_user(callback_query.from_user.id))
    user[2] = 1
    user[3] = ''
    await db.update_profile(callback_query, user)
    text = "Замечательно\nНайдите себя в списке:\n"
    text += f"<i>\nСтраница <b>{pag + 1}</b></i>"
    if isinstance(callback_query, types.CallbackQuery):
        await callback_query.answer()
        # await callback_query.message.delete()
        await callback_query.message.edit_text(text, reply_markup=i_kb.as_markup())
    else:
        await callback_query.message.answer(text, reply_markup=i_kb.as_markup())


@router.callback_query(cb_teacher.filter())
async def reg_teacher(callback_query: types.CallbackQuery, callback_data: cb_teacher, db: DB, bot: Bot):
    user = list(await db.get_user(callback_query.from_user.id))
    user[3] = callback_data.name
    await db.update_profile(callback_query, user)
    await callback_query.answer()

    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Расписание", callback_data=cb_days(date=datetime.date.today().strftime('%d.%m.%Y')).pack()))
    kb.add(InlineKeyboardButton(text="Назад", callback_data=cb_pag_teacher(pag=0).pack()))
    kb.adjust(1)
    text = f"""Супер! \nРегистрация прошла успешно\n<i>Поиск по преподавателю ({user[3]})</i> \n\nТак же /communication позволит Вам узнать номера деканата и кафедр и связаться с нами если обнаружите ошибку :)"""
    try:
        await callback_query.message.edit_text(text, reply_markup=kb.as_markup())
    except Exception:
        await callback_query.message.answer(text, reply_markup=kb.as_markup())


@router.callback_query(cb_group.filter())
async def user_reg(callback_query: types.CallbackQuery, callback_data: cb_group, db: DB):
    db.create_table_users()
    await db.create_profile_student(callback_query, callback_data.kurs, callback_data.group)
    user = list(await db.get_user(callback_query.from_user.id))
    user[0] = callback_data.kurs
    user[1] = callback_data.group
    user[2] = 0
    await db.update_profile(callback_query, user)
    await callback_query.answer()
    # await callback_query.message.delete()

    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="Расписание", callback_data=cb_days(date=datetime.date.today().strftime('%d.%m.%Y')).pack()))
    kb.add(InlineKeyboardButton(text="Назад", callback_data=cb_kurs(kurs=user[0]).pack()))
    kb.adjust(1)
    text = (f"Супер! \nРегистрация прошла успешно\n<i>Поиск по группе ({user[0]}: {user[1]})</i>"
            f"\n\n"
            f"Так же /communication позволит Вам узнать номера деканата и кафедр и связаться с нами если обнаружите ошибку :)")
    try:
        await callback_query.message.edit_text(text, reply_markup=kb.as_markup())
    except Exception:
        await callback_query.message.answer(text, reply_markup=kb.as_markup())


@router.callback_query(F.data=="Нет")
async def callback_no(callback_query: types.CallbackQuery, db: DB):
    user = list(await db.get_user(callback_query.from_user.id))
    if user[2] == 0:
        user[2] = 1
        text = f"Успешно \nПоиск по преподавателю ({user[3]})"
    else:
        user[2] = 0
        text = f"Успешно \nПоиск по группе ({user[0]}: {user[1]})"
    await db.update_profile(callback_query, user)
    await callback_query.answer()
    # await callback_query.message.delete()
    try:
        await callback_query.message.edit_text(text)
    except Exception:
        await callback_query.message.answer(text)
