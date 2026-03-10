from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import datetime, timedelta


class days_callback(CallbackData, prefix="switch_one_day"):
    move: int

class to_date_callback(CallbackData, prefix="date"):
    date: str

class to_week_callback(CallbackData, prefix="week_shedule"):
    date: str

class week_callback(CallbackData, prefix="switch_one_week"):
    move: int

class register_callback(CallbackData, prefix="registration"): ...

class im_teacher_callback(CallbackData, prefix="im_a_teacher"): ...

class level_callback(CallbackData, prefix="study_level"):
    level: str

class year_callback(CallbackData, prefix="study_year"):
    year: int
    level: str
    cache: str

class student_register_callback(CallbackData, prefix="student_end_register"):
    group_id: int

TODAY = InlineKeyboardButton(text="На сегодня", callback_data=to_date_callback(date=datetime.today().strftime("%d-%m-%Y")).pack())
TOMOROW = InlineKeyboardButton(text="На завтра", callback_data=to_date_callback(
    date=(datetime.today() + timedelta(1)).strftime("%d-%m-%Y")).pack()
)
WEEK = InlineKeyboardButton(text="На неделю", callback_data=to_week_callback(date=datetime.today().strftime("%d-%m-%Y")).pack())
NEXT_WEEK = InlineKeyboardButton(text="На следующую", callback_data=to_week_callback(
    date=(datetime.today() + timedelta(7)).strftime("%d-%m-%Y")).pack()
)

def leaf_buttons() -> InlineKeyboardBuilder:
    key_builder = InlineKeyboardBuilder()
    key_builder.add(InlineKeyboardButton(text="👈", callback_data=days_callback(move=-1).pack()))
    key_builder.add(InlineKeyboardButton(text="👉", callback_data=days_callback(move=1).pack()))
    key_builder.add(TODAY, TOMOROW, WEEK)
    key_builder.adjust(2, 2, 1)
    return key_builder

def leaf_week_buttons() -> InlineKeyboardBuilder:
    key_builder = InlineKeyboardBuilder()
    key_builder.add(InlineKeyboardButton(text="👈", callback_data=week_callback(move=-1).pack()))
    key_builder.add(InlineKeyboardButton(text="👉", callback_data=week_callback(move=1).pack()))
    key_builder.add(TODAY, TOMOROW)
    key_builder.adjust(2, 2, 1)
    return key_builder

def student_menu() -> InlineKeyboardBuilder:
    key_builder = InlineKeyboardBuilder()
    key_builder.add(TODAY, TOMOROW, WEEK)
    key_builder.adjust(2, 1)
    return key_builder