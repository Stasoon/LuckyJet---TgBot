import os
from typing import Final
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


CODE_WORD = 'BOTJET11'


class Config:
    TOKEN: Final = os.getenv('BOT_TOKEN', 'Впишите токен в .env!')
    ADMIN_IDS: Final = tuple(int(i) for i in str(os.getenv('BOT_ADMIN_IDS')).split(','))

    __BOT_USERNAME = 'bot_username'

    @classmethod
    def set_bot_username(cls, username: str) -> None:
        cls.__BOT_USERNAME = username

    @classmethod
    def get_bot_username(cls) -> str:
        return cls.__BOT_USERNAME

    LOCALES_DIR = 'locales'
    I18N_DOMAIN = 'bot'

    DEBUG: Final = bool(os.getenv('DEBUG'))
