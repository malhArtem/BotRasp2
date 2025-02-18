import asyncio
import os

from aiogram import Router, F, types, Bot

from config import admins_id
from db import DB
from parse.excel import parse_xl, parse_spo

router = Router()



@router.message(F.document)  # отлавливаем сообщения являющиеся документом
async def get_file_xl(message: types.Message, bot: Bot, db: DB):
    if str(message.from_user.id) == str(message.chat.id) == admins_id:
        if message.document.file_name.split('.')[-1] == 'xlsx':
            if message.caption and message.caption == "ВО":
                file_id = message.document.file_id
                file = await bot.get_file(file_id)
                path_file = file.file_path
                path = 'xl_new.xlsx'
                await bot.download_file(path_file, path)  # скачиваем файл и сохраняем под именем 'xl_new.xlsx'

                if os.path.exists('xl_old.xlsx'):
                    os.remove('xl_old.xlsx')

                if os.path.exists('xl.xlsx'):
                    os.rename('xl.xlsx', 'xl_old.xlsx')

                os.rename('xl_new.xlsx', 'xl.xlsx')

                await db.delete_old()

                kurses = await db.get_kurs()
                for kurs in kurses:
                    if kurs[1] != 'users' and kurs[1] != 'СПО':
                        await db.rename_tables(kurs[1])  # переименовывываем уже существующие таблицы с расписанием
                await message.answer('Изменяем раписание')
                parce = asyncio.create_task(parse_xl(message, db))# извлекаем данные из нового excel файла в базу данных
                # await message.answer('Расписание изменено')
                # await get_all_diff()                             # сравниваем старое расписание с новым и отправляем различия пользователям

            elif message.caption and message.caption == "СПО":
                print("СПО")
                file_id = message.document.file_id
                file = await bot.get_file(file_id)
                path_file = file.file_path
                path = 'spo_new.xlsx'
                await bot.download_file(path_file, path)

                if os.path.exists('spo_old.xlsx'):
                    os.remove('spo_old.xlsx')

                if os.path.exists('spo.xlsx'):
                    os.rename('spo.xlsx', 'spo_old.xlsx')

                os.rename('spo_new.xlsx', 'spo.xlsx')

                await db.delete_old_spo()

                kurses = await db.get_kurs()
                for kurs in kurses:
                    if kurs[1] == "СПО":
                        await db.rename_tables("СПО")

                await message.answer('Изменяем раписание')
                parse_spo(db)
                await message.answer('Расписание изменено')

        else:
            await message.answer('Неправильное разрешение')
