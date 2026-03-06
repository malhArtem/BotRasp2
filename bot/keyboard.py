from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from typing import Literal
from datetime import datetime

class days_callback(CallbackData, prefix="move"):
    move: Literal[-1, 1]

LEAF_BUTTONS = [
    InlineKeyboardButton(text="👈", callback_data=days_callback(move=-1).pack()),
    InlineKeyboardButton(text="👉", callback_data=days_callback(move=1).pack())
]

def leaf_buttons(builder: InlineKeyboardBuilder):
    back_button = InlineKeyboardButton(text="👈", callback_data=days_callback(move=-1).pack())
    forward_button = InlineKeyboardButton(text="👉", callback_data=days_callback(move=1).pack())
    builder.row(back_button, forward_button)
    return builder

class im_teacher_callback(CallbackData, prefix="im_a_teacher"): ...

class level_callback(CallbackData, prefix="study_level"):
    level: str

class year_callback(CallbackData, prefix="study_year"):
    year: int
    level: str
    cache: str

class student_register_callback(CallbackData, prefix="student_end_register"):
    group_id: int


class cb_kurs(CallbackData, prefix="kurs"):
    kurs: str


class cb_month(CallbackData, prefix="month"):
    month: int


class cb_group(CallbackData, prefix="group"):
    kurs: str
    group: str


class cb_day(CallbackData, prefix="day"):
    month: int
    day: int


class cb_teacher(CallbackData, prefix="teacher"):
    name: str


class cb_pag_teacher(CallbackData, prefix="pag"):
    pag: int

class to_date_callback(CallbackData, prefix="date"):
    date: datetime