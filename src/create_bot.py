from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from src.middlewares.localization import setup_middleware

from config import Config


bot = Bot(token=Config.TOKEN, parse_mode='html')
Bot.set_current(bot)

storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

# Настроим i18n middleware для работы с многоязычностью
i18n = setup_middleware(dp)
# Создадим псевдоним для метода gettext
_ = i18n.gettext

