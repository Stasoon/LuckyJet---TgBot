from aiogram import executor

from src.filters import register_all_filters
from src.handlers import register_all_handlers
from src.database import register_models
from src.create_bot import dp, bot
from config import Config
from src.utils import logger


async def on_startup(_):
    bot_username = (await bot.get_me()).username
    Config.set_bot_username(bot_username)

    # Регистрация фильтров
    register_all_filters(dp)

    # Регистрация хэндлеров
    register_all_handlers(dp)

    # Регистрация моделей базы данных
    register_models()

    logger.info('Бот запущен!')


async def on_shutdown(_):
    await (await bot.get_session()).close()
    if not Config.DEBUG:
        for admin_id in Config.ADMIN_IDS:
            await bot.send_message(chat_id=admin_id, text='<b>Бот остановлен!</b>')


def start_bot():
    try:
        executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
    except Exception as e:
        logger.error(e)
