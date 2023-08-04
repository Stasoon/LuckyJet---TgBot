from aiogram import Bot
from aiogram.types import CallbackQuery, ChatMemberStatus
from aiogram.utils.exceptions import Unauthorized, ChatNotFound, BotKicked
from aiogram.dispatcher.filters import BoundFilter

from src.database.channel import get_channel_ids
from src.utils import logger


class IsSubFilter(BoundFilter):
    """
    Custom filter "is_sub".
    """
    key = "is_sub"

    def __init__(self, is_sub: bool = True):
        self.is_sub = is_sub

    async def check(self, callback: CallbackQuery):
        for channel_id in get_channel_ids():
            if not await self.__check_status_is_member(callback.bot, channel_id, callback.from_user.id):
                return self.is_sub is False
        return self.is_sub is True

    @staticmethod
    async def __check_status_is_member(bot: Bot, channel_id: int, user_id: int):
        try:
            user = await bot.get_chat_member(channel_id, user_id)
            if user.status != ChatMemberStatus.LEFT:
                return True
            return False
        except (Unauthorized, ChatNotFound, BotKicked) as e:
            logger.exception(e)
            return True
