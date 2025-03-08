from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject

from bot.keyboard import cb_days

steps: Dict[int, list] = {}

class StepsCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        callback = data.get('callback_data')
        if callback is None:
            callback = event.data
        user = event.from_user.id
        user_steps = steps.setdefault(user, [])
        if len(user_steps) >= 2 and callback == user_steps[-2]:
            user_steps.pop()
        else:
            if not isinstance(callback, cb_days) or callback.is_step:
                user_steps.append(callback)
            if len(user_steps) > 10:
                user_steps.pop(0)
        print(user_steps)
        data['last_step'] = user_steps[-2] if len(user_steps) >=2 else None
        result = await handler(event, data)
        return result


class StepsMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any]
    ) -> Any:
        steps[event.from_user.id] = []
        data['last_step'] = None
        result = await handler(event, data)
        return result
