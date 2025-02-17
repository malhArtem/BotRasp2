from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("communication"))
async def connection_cmd(message: types.Message):
    text = """ <b>1. Деканат</b> (каб. 333а) | Тел: <code>2-208-460</code>; <code>2-208-553</code>  
<b>2. КАиММГ</b> (каб. 334) | Тел: <code>2-208-641</code>
<b>3. КМА</b> (каб. 332) | Тел: <code>2-208-690</code>  
<b>4. КММ</b> (каб. 322) | Тел: <code>2-208-364</code>
<b>5. КТФ</b> (каб. 324) | Тел: <code>2-208-665</code>  
<b>6. КУЧП</b> (каб. 327, 308) | Тел: <code>2-208-618</code>
<b>7. КФА</b> (каб. 225) | Тел: <code>2-208-771</code>

Сообщить об ошибке: @mlhv_artem
"""
    await message.answer(text)
