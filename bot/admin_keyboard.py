from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

def admin_panel() -> InlineKeyboardBuilder:
    key_builder = InlineKeyboardBuilder()
    key_builder.add(
        InlineKeyboardButton(text="Добавить преподавателя", callback_data=add_teacher_callback().pack())
    )
    key_builder.add(
        InlineKeyboardButton(text="Добавить группу", callback_data=add_group_callback().pack())
    )
    key_builder.add(
        InlineKeyboardButton(text="Добавить пару", callback_data=add_pair_callback().pack())
    )
    key_builder.adjust(1)
    return key_builder

class add_teacher_callback(CallbackData, prefix="add_teacher"): ...
class add_group_callback(CallbackData, prefix="add_group"): ...
class add_pair_callback(CallbackData, prefix="add_pair"): ...