import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton


def leaf_kb(builder, date):
    ib1 = InlineKeyboardButton(text="👈", callback_data=cb_days(
        date=(date - datetime.timedelta(days=1)).strftime('%d.%m.%Y')).pack())
    ib2 = InlineKeyboardButton(text="👉", callback_data=cb_days(
        date=(date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')).pack())
    builder.row(ib1, ib2)
    return builder


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


class cb_days(CallbackData, prefix="date"):
    date: str

# cb_kurs = CallbackData("kurs", "number")
# cb_group = CallbackData("group", "kurs", "groups")
# cb_month = CallbackData("month", "number")
# cb_day = CallbackData("day", "month", "number")
# cb_teacher = CallbackData("teacher", "name")
#
# cb_pag_teacher = CallbackData("pag_teacher", "pag")
#
# cb_days = CallbackData("days", "date")