from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types
from config import Config

from src.database.user import get_locale


async def get_lang(user_id):
    lang_code = get_locale(user_id)
    return lang_code


class ACLMiddleware(I18nMiddleware):
    # Каждый раз, когда нужно узнать язык пользователя - выполняется эта функция
    async def get_user_locale(self, action, args):
        user = types.User.get_current()
        # Возвращаем язык из базы ИЛИ (если не найден) - язык из Телеграма
        return await get_lang(user.id) or user.locale


def setup_middleware(dp):
    # Устанавливаем миддлварь
    i18n = ACLMiddleware(Config.I18N_DOMAIN, Config.LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
