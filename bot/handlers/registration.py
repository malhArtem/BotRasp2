import asyncio

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cashews import cache

from bot import keyboard
import database.db as db
import core.models as models
import parse.utils as utils
import core.errors as errors
from core.config import config

router = Router()
cache.setup("mem://") # используем память

@cache(ttl="1m", key="groups:{key}") #cache либа будет использовать 2 аргумент как ключ
async def get_groups(database: db.DataBase, key: str) -> list[models.Group]: 
    async with database.db_cursor(False) as cursor:
        return await db.GroupsBase.get_groups(cursor)

async def show_register(message: types.Message, edit: bool = False) -> None:
    register_message = "Здравствуй, математик!\nПройди небольшую регистрацию и сможешь наблюдать свое расписание.\nВыбери свою ступень образования:"
    key_builder = InlineKeyboardBuilder()

    for level in config.study_levels:
        key_builder.add(
            InlineKeyboardButton(text=level, callback_data=keyboard.level_callback(level=level).pack())
        )
    key_builder.add(
        InlineKeyboardButton(text="Преподаватель", callback_data=keyboard.im_teacher_callback().pack())
    )
    key_builder.adjust(1)

    if edit:
        await message.edit_text(
            text=register_message,
            reply_markup=key_builder.as_markup()
        )
    else:
        await message.answer(
            text=register_message,
            reply_markup=key_builder.as_markup()
        )

@router.message(Command('start', 'register'))
async def register_handler(message: types.Message, database: db.DataBase):
    await message.delete()
    try:
        async with database.db_cursor(False) as cursor:
            profile = await db.UsersBase.get_profile(cursor, message.from_user.id)
            print(profile)

    except errors.UserNotFoundError:
        await show_register(message)

    else:
        await message.answer(
            "Perfecto! Что будем делать?",
            reply_markup=keyboard.student_menu().as_markup()
        )

@router.callback_query(keyboard.register_callback.filter())
async def register_callback(callback: types.CallbackQuery):
    await show_register(callback.message, True)
    await callback.answer()

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
        text="Замечательно!\nВыбери свой курс:",
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
        text="Превосходно!!!\nВыбери своё направление:",
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
        text="Гениально!!!!! Вы успешно зарегестрировались в сервисе.\nЧто делаем дальше?"
    )
    await callback_query.answer()
    



# @router.callback_query(_.filter())
# async def user_reg_teach(callback_query: types.CallbackQuery, callback_data: cb_pag_teacher, db: DB):
#     db.create_table_users()

#     i_kb = InlineKeyboardBuilder()
#     teachers = await db.get_teachers()
#     teachers.sort()

#     pag = callback_data.pag

#     start = pag * 24
#     stop = (pag + 1) * 24 if (pag + 1) * 24 < len(teachers) else len(teachers)
#     for i in range(start, stop):
#         ib = InlineKeyboardButton(text=str(teachers[i][0]), callback_data=cb_teacher(name=str(teachers[i][0])).pack())
#         i_kb.add(ib)
#     i_kb.adjust(2)
#     spec_buttons = []

#     if pag > 0:
#         ib = InlineKeyboardButton(text="👈", callback_data=cb_pag_teacher(pag=pag - 1).pack())
#         spec_buttons.append(ib)

#     ib_back = InlineKeyboardButton(text="Назад", callback_data='kurs')
#     spec_buttons.append(ib_back)
#     if stop != len(teachers):
#         ib = InlineKeyboardButton(text="👉", callback_data=cb_pag_teacher(pag=pag + 1).pack())
#         spec_buttons.append(ib)

#     i_kb.row(*spec_buttons)

#     # db.create_table_users()
#     await db.create_profile_teacher(callback_query, '')
#     user = list(await db.get_user(callback_query.from_user.id))
#     user[2] = 1
#     user[3] = ''
#     await db.update_profile(callback_query, user)
#     text = "Замечательно\nНайдите себя в списке:\n"
#     text += f"<i>\nСтраница <b>{pag + 1}</b></i>"
#     if isinstance(callback_query, types.CallbackQuery):
#         await callback_query.answer()
#         # await callback_query.message.delete()
#         await callback_query.message.edit_text(text, reply_markup=i_kb.as_markup())
#     else:
#         await callback_query.message.answer(text, reply_markup=i_kb.as_markup())


# @router.callback_query(cb_teacher.filter())
# async def reg_teacher(callback_query: types.CallbackQuery, callback_data: cb_teacher, db: DB, bot: Bot):
#     user = list(await db.get_user(callback_query.from_user.id))
#     user[3] = callback_data.name
#     await db.update_profile(callback_query, user)
#     await callback_query.answer()

#     kb = InlineKeyboardBuilder()
#     kb.add(InlineKeyboardButton(text="Расписание", callback_data=cb_days(date=datetime.date.today().strftime('%d.%m.%Y')).pack()))
#     kb.add(InlineKeyboardButton(text="Назад", callback_data=cb_pag_teacher(pag=0).pack()))
#     kb.adjust(1)
#     text = f"""Супер! \nРегистрация прошла успешно\n<i>Поиск по преподавателю ({user[3]})</i> \n\nТак же /communication позволит Вам узнать номера деканата и кафедр и связаться с нами если обнаружите ошибку :)"""
#     try:
#         await callback_query.message.edit_text(text, reply_markup=kb.as_markup())
#     except Exception:
#         await callback_query.message.answer(text, reply_markup=kb.as_markup())


# @router.callback_query(cb_group.filter())
# async def user_reg(callback_query: types.CallbackQuery, callback_data: cb_group, db: DB):
#     db.create_table_users()
#     await db.create_profile_student(callback_query, callback_data.kurs, callback_data.group)
#     user = list(await db.get_user(callback_query.from_user.id))
#     user[0] = callback_data.kurs
#     user[1] = callback_data.group
#     user[2] = 0
#     await db.update_profile(callback_query, user)
#     await callback_query.answer()
#     # await callback_query.message.delete()

#     kb = InlineKeyboardBuilder()

#     kb.add(InlineKeyboardButton(text="Расписание", callback_data=cb_days(date=datetime.date.today().strftime('%d.%m.%Y')).pack()))
#     kb.add(InlineKeyboardButton(text="Назад", callback_data=cb_kurs(kurs=user[0]).pack()))
#     kb.adjust(1)
#     text = (f"Супер! \nРегистрация прошла успешно\n<i>Поиск по группе ({user[0]}: {user[1]})</i>"
#             f"\n\n"
#             f"Так же /communication позволит Вам узнать номера деканата и кафедр и связаться с нами если обнаружите ошибку :)")
#     try:
#         await callback_query.message.edit_text(text, reply_markup=kb.as_markup())
#     except Exception:
#         await callback_query.message.answer(text, reply_markup=kb.as_markup())


# @router.callback_query(F.data=="Нет")
# async def callback_no(callback_query: types.CallbackQuery, db: DB):
#     user = list(await db.get_user(callback_query.from_user.id))
#     if user[2] == 0:
#         user[2] = 1
#         text = f"Успешно \nПоиск по преподавателю ({user[3]})"
#     else:
#         user[2] = 0
#         text = f"Успешно \nПоиск по группе ({user[0]}: {user[1]})"
#     await db.update_profile(callback_query, user)
#     await callback_query.answer()
#     # await callback_query.message.delete()
#     try:
#         await callback_query.message.edit_text(text)
#     except Exception:
#         await callback_query.message.answer(text)
