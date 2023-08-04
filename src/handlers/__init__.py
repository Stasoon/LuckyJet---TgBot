from aiogram import Dispatcher

from .admin.admin import register_admin_handlers
from .user.user import register_user_handlers


def register_all_handlers(dp: Dispatcher):
    # сюда прописывать импортированные функции
    handlers = (
        register_admin_handlers,
        register_user_handlers,
    )
    for handler in handlers:
        handler(dp)
