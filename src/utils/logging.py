from loguru import logger

from config import Config


def setup_logger():
    if not Config.DEBUG:
        logger.add("logs/logs.log", format="{time} {level} {message}", rotation="10:00", compression="zip")
