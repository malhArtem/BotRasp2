from database.get_shedule import get_shedule
from datetime import timedelta

import core.models as models
import database.db as db
from core.config import config

async def get_parsed_shedule(user_id: int, database: db.DataBase):
    shedule = await get_shedule(user_id, database)
    if shedule.owner == "TEACHER":
        parsed = _parse_teacher_shedule(shedule)
    else:
        parsed = _parse_student_shedule(shedule)
    return parsed

def _parse_teacher_shedule(shedule: models.Shedule) -> dict[str, dict[str, str]]:
    teacher_fio = ""
    if shedule.numerator: teacher_fio = shedule.numerator[0].teacher_id
    elif shedule.denumerator: teacher_fio = shedule.denumerator[0].teacher_id
    
    free_day_message = f"👨‍🏫 {teacher_fio}\nПар не запланированно 🎉\nМожно отдохнуть 💤"
    parsed = {}

    days = dict(zip(config.days_to_numbers, [free_day_message]*len(config.days_to_numbers)))
    for pair in shedule.numerator:
        if days[pair.day].endswith("💤"): days[pair.day] = f"👨‍🏫 {teacher_fio}\n"
        end_time = pair.time + timedelta(minutes=95) # длинна пары
        days[pair.day] += f"```\n🕙 {pair.time.strftime("%H:%M") - {end_time.strftime("%H:%M")}}\n"
        days[pair.day] += f"👥 {pair.group_code} | {pair.year} курс\n"
        days[pair.day] += f"📚 {pair.subject}\n"
        days[pair.day] += f"📍 {pair.auditory}\n```\n"
    parsed["Числитель"] = days

    days = dict(zip(config.days_to_numbers, [free_day_message]*len(config.days_to_numbers)))
    for pair in shedule.denumerator:
        if days[pair.day].endswith("💤"): days[pair.day] = f"👨‍🏫 {teacher_fio}\n"
        end_time = pair.time + timedelta(minutes=95) # длинна пары
        days[pair.day] += f"```\n🕙 {pair.time.strftime("%H:%M") - {end_time.strftime("%H:%M")}}\n"
        days[pair.day] += f"👥 {pair.group_code} | {pair.year} курс\n"
        days[pair.day] += f"📚 {pair.subject}\n"
        days[pair.day] += f"📍 {pair.auditory}\n```\n"
    parsed["Знаменатель"] = days

    return parsed
        

def _parse_student_shedule(shedule: models.Shedule) -> dict[str, dict[str, str]]:
    group = ""
    if shedule.numerator: group = shedule.numerator[0].group
    elif shedule.denumerator: group = shedule.denumerator[0].group

    free_day_message = f"🧑‍🎓 {group}\nПар не наблюдается 🎉\nСидим не рыпаемся 💤"
    parsed = {}

    days = dict(zip(config.days_to_numbers, [free_day_message]*len(config.days_to_numbers)))
    for pair in shedule.numerator:
        if days[pair.day].endswith("💤"): days[pair.day] = f"🧑‍🎓 {group}\n"
        end_time = pair.time + timedelta(minutes=95) # длинна пары
        days[pair.day] += f"```\n🕙 {pair.time.strftime("%H:%M") - {end_time.strftime("%H:%M")}}\n"
        days[pair.day] += f"👨‍🏫 {pair.teacher_fio}\n"
        days[pair.day] += f"📚 {pair.subject}\n"
        days[pair.day] += f"📍 {pair.auditory}\n```\n"
    parsed["Числитель"] = days

    days = dict(zip(config.days_to_numbers, [free_day_message]*len(config.days_to_numbers)))
    for pair in shedule.denumerator:
        if days[pair.day].endswith("💤"): days[pair.day] = f"🧑‍🎓 {group}\n"
        end_time = pair.time + timedelta(minutes=95) # длинна пары
        days[pair.day] += f"```\n🕙 {pair.time.strftime("%H:%M") - {end_time.strftime("%H:%M")}}\n"
        days[pair.day] += f"👨‍🏫 {pair.teacher_fio}\n"
        days[pair.day] += f"📚 {pair.subject}\n"
        days[pair.day] += f"📍 {pair.auditory}\n```\n"
    parsed["Знаменатель"] = days
    return parsed