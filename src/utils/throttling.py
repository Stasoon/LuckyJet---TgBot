from functools import wraps

from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.handler import CancelHandler

from src.create_bot import dp


def throttle(rate: float = 2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            action = args[0]

            if isinstance(action, CallbackQuery):
                message = action.message
                key = action.data
                user_id = action.from_user.id
            else:
                message = action
                key = message.text
                user_id = message.from_id

            try:
                await dp.throttle(key=key, rate=rate, user_id=user_id)
            except Throttled as throttled:
                if throttled.exceeded_count == 2:
                    await message.answer('Слишком много запросов! Пожалуйста, не нажимайте так часто.')
                raise CancelHandler
            else:
                await func(*args, **kwargs)

        return wrapper
    return decorator
