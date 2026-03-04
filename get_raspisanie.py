import datetime

from aiogram import types

from config import config
from db import DB
from parse.utils import chisl_or_znam, normalize


async def get_teach_rasp(day, message, db: DB):
    user = await db.get_user(message.from_user.id)
    rasp = list()
    kurses = await db.get_kurs()
    ch_or_zn = chisl_or_znam(day)
    for kurs in kurses:
        if kurs[1] != "users" and not ('old' in kurs[1]):
            if ch_or_zn == 4:
                db.cur.execute("SELECT *, '{}' FROM '{}' WHERE day = '{}' AND teach1 = '{}' ".format(kurs[1], kurs[1],
                                                                                                  day.weekday(),
                                                                                                  user[3]))
            else:
                db.cur.execute("SELECT *, '{}' FROM '{}' WHERE day = '{}' and teach3 = '{}' ".format(kurs[1], kurs[1],
                                                                                                  day.weekday(),
                                                                                                  user[3]))
            rasp1 = list(db.cur.fetchall())
            rasp.extend(rasp1)

    rasp = sorted(rasp, key=lambda para: datetime.datetime.strptime(para[1].split('-')[0], '%H.%M'))

    temp_rasp = []
    [temp_rasp.append(x) for x in rasp if x not in temp_rasp]
    rasp = temp_rasp
    text = text = f'📆 <b><u>{config.number_in_days.get(day.weekday())}</u></b>'
    text = f'<i>{user[3]}   [{day.strftime("%d.%m.%Y")}]</i>\n' + text
    if ch_or_zn == 4:
        text = text + '(числитель):\n'
    else:
        text = text + '(знаменатель):\n'
    if len(rasp) == 0:
        text = text + "\nНа сегодня занятий не наблюдается...\nОтличный день для отдыха!"
        return text
    k = 0

    for i in range(0, len(rasp)):
        if k != 0 and rasp[i][1] != rasp[i - 1][1]:
            text = text + f'\n📍 {rasp[i - 1][ch_or_zn + 2]}</blockquote>'
            k = 0

        if rasp[i][ch_or_zn] is not None:
            if rasp[i][1] != rasp[i - 1][1] or i == 0:
                text = text + f'\n<blockquote>🕙 <b><i>{rasp[i][1]}</i>:</b>\n'
                text = text + (f'📚 {normalize(rasp[i][ch_or_zn])} \n'
                               f'👥 {rasp[i][10]}: {rasp[i][3]}')
                k += 1
            else:
                text = text + f', {rasp[i][3]}'
    if k != 0:
        text = text + f'\n📍 {rasp[len(rasp) - 1][ch_or_zn + 2]}</blockquote>'
        k = 0
    return text


async def student_rasp(message: types.Message, day, db: DB):
    user = await db.get_user(message.from_user.id)
    ch_or_zn = chisl_or_znam(day)  # узнаем какая сейчас неделя: числитель или знаменатель
    rasp = list(await db.get_rasp(day.weekday(), user[0],
                               user[1]))  # получаем данные из базы данных, где нужный день недели, курс и группа
    # temp_rasp = []
    # [temp_rasp.append(x) for x in rasp if x not in temp_rasp]
    # rasp = temp_rasp
    text = f'📆 {day.strftime("%d.%m.%Y")}\n'
    text += f'⏳ <u><b>{config.number_in_days.get(day.weekday())}</b></u>'
    if ch_or_zn == 4:
        text = text + ' | числитель\n'
    else:
        text = text + ' | знаменатель\n'
    text += f'👥 {user[0]} | {user[1]}\n'

    # text += f'{day.strftime("%d.%m.%Y")}\n'

    j = 1

    for l in range(1, len(rasp)):
        if rasp[0][1] == rasp[l][1]:
            j += 1

    for m in range(len(rasp) // j):
        for k in range(j):
            i = m + (len(rasp) // j) * k
            if (rasp[i][ch_or_zn] is not None and (rasp[i][ch_or_zn] != rasp[m + (len(rasp) // j) * (k - 1)][
                ch_or_zn] or rasp[i][ch_or_zn + 1] != rasp[m + (len(rasp) // j) * (k - 1)][
                                                       ch_or_zn + 1] or rasp[i][ch_or_zn + 2] !=
                                                   rasp[m + (len(rasp) // j) * (k - 1)][
                                                       ch_or_zn + 2])) or (rasp[i][ch_or_zn] is not None and k == 0):
                text = text + f"\n<blockquote>🕙 <b><i>{rasp[i][1]}</i>:</b>\n"

                text += f"📚 {normalize(rasp[i][ch_or_zn])}"
                if rasp[i][ch_or_zn + 1]:
                    text += f'\n👨‍🏫 {normalize(rasp[i][ch_or_zn + 1])}'
                if rasp[i][ch_or_zn + 2]:
                    text += f'\n📍 {normalize(rasp[i][ch_or_zn + 2])}'

                if k > 0:
                    text = text + f"({k + 1})</blockquote>"
                else:
                    text = text + "</blockquote>"

    pairs = [day[ch_or_zn] for day in rasp ]
    if not rasp or not any(pairs):
        text += "\n<blockquote>Сегодня отличный день для отдыха</blockquote>\n"

    return text