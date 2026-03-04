from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class UserProfile(BaseModel):
    id: str
    username: str
    full_name: str
    year: int
    group: str
    is_teacher: int
    teacher_id: int

class UserStudent(UserProfile):
    is_teacher: Literal[0] = 0
    teacher_id: Literal[None] = None

    year: int
    group: str

class UserTeacher(UserProfile):
    is_teacher: Literal[1] = 1
    year: Literal[0] = 0
    group: Literal[""] = ""

    teacher_id: int | None = None

class Teacher(BaseModel):
    id: int
    FIO: str

class Pair(BaseModel):
    group: str
    day: str
    time: datetime
    subject: str
    auditory: str
    week_type: Literal["NUMERATOR", "DENUMERATOR"]
    teacher: str

class Shedule(BaseModel):
    numerator: list[Pair]
    dennumerator: list[Pair]

class StudentShedule(Shedule):
    owner: Literal["STUDENT", "TEACHER"] = "STUDENT"

class TeacherShedule(Shedule):
    owner: Literal["STUDENT", "TEACHER"] = "TEACHER"