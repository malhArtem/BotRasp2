from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class BaseUser(BaseModel):
    id: str
    username: str
    full_name: str

class Student(BaseUser):
    is_teacher: Literal[0] = 0
    teacher_id: Literal[None] = None

    year: int
    group: str

class Teacher(BaseUser):
    is_teacher: Literal[1] = 1
    year: Literal[0] = 0
    group: Literal[""] = ""

    teacher_id: int | None = None


class Pair(BaseModel):
    group: str
    day: str
    time: datetime
    subject: str
    auditory: str
    teacher: str


    