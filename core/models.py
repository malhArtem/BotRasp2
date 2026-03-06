from pydantic import BaseModel
from typing import Literal, Generic, TypeVar
from datetime import datetime

WEEK_DAYS = Literal[
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота"
]

STUDY_LEVELS = Literal[
    "СПО",
    "Бакалавриат",
    "Магистратура"
]

ROLES = Literal["STUDENT", "TEACHER"]


pairType = TypeVar("pairType", StudentPair, TeacherPair)

class UserProfile(BaseModel):
    """
    user_id: telegram id\n
    username: telegram username\n
    full_name: telegram name\n
    group_id: ref. to group table or None\n
    teacher_id: ref. on teachers table or None
    """

    user_id: str
    username: str
    full_name: str
    group_id: int
    teacher_id: int

class Teacher(BaseModel):
    """
    teacher_id: iternal base id or None\n
    FIO: family name and subname of teacher
    """
    teacher_id: int | None = None
    FIO: str

class Pair(BaseModel):
    """
    pair_id: iternal base id or None\n
    day: name of weakday\n
    time: ISO format\n
    subject: pair subject\n
    auditory: auditory number\n
    week_type: numerator/denumerator\n
    group_id: ref. on group table\n
    teacher_id: ref. on teachers table
    """

    pair_id: int | None = None
    day: WEEK_DAYS
    time: datetime
    subject: str
    auditory: str
    week_type: Literal["NUMERATOR", "DENUMERATOR"]
    group_id: int
    teacher_id: int

class StudentPair(Pair):
    teacher_fio: str

class TeacherPair(Pair):
    group_code: str
    year: int

class Group(BaseModel):
    """
    group_id: iternal group id or None\n
    level: styding level\n
    year: year of studing\n
    code: speciality abbriviature and group num. e.g. ISAP2
    """
    group_id: int | None = None
    level: STUDY_LEVELS
    year: int
    code: str

class Shedule(BaseModel, Generic(pairType)):
    numerator: list[pairType]
    denumerator: list[pairType]

class StudentShedule(Shedule[StudentPair]):
    owner: ROLES = "STUDENT"

class TeacherShedule(Shedule[TeacherPair]):
    owner: ROLES = "TEACHER"