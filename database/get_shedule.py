from collections import defaultdict

from core.config import config
import core.models as models
import database.db as db

def _devide_shedule(pairs: list[models.Pair]) -> dict:
    shedule = {
        "NUMERATOR": defaultdict(list),
        "DENUMERATOR": defaultdict(list)
    }

    for pair in pairs:
        if pair.week_type == "NUMERATOR":
            shedule["NUMERATOR"][pair.day].append(pair)
        else:
            shedule["DENUMERATOR"][pair.day].append(pair)

    for week_type, pairs in shedule.items():
        shedule[week_type] = sorted(
            shedule[week_type],
            key=lambda pair: pair.time.timestamp()
        )

    return shedule

async def get_shedule(user_id: int, database: db.DataBase) -> models.TeacherShedule | models.StudentShedule:
    async with database.db_cursor(False) as cursor:
        profile = await db.UsersBase.get_profile(cursor, user_id)
        if profile.is_teacher:
            pairs = await db.ShedulesBase.get_teacher_pairs(cursor, profile.teacher_id)
        else:
            pairs = await db.ShedulesBase.get_student_pairs(cursor, profile.group)

    raw_shedule = _devide_shedule(pairs)
    if profile.is_teacher:
        return models.TeacherShedule(
            numerator=raw_shedule["NUMERATOR"],
            denumerator=raw_shedule["DENUMERATOR"]
        )
    else:
        return models.StudentShedule(
            numerator=raw_shedule["NUMERATOR"],
            denumerator=raw_shedule["DENUMERATOR"]
        )