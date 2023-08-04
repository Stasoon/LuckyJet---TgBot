from aiogram import Bot
from aiogram.types import ChatMemberStatus, InlineKeyboardMarkup
from aiogram.utils.exceptions import Unauthorized, ChatNotFound, BotKicked

from src.database.channel import get_channels_full_data
from src.utils import logger
from src.handlers.user.kb import Keyboards


async def get_notsubbed_channels_markup_or_none(bot: Bot, user_id: int) -> InlineKeyboardMarkup | None:
    not_subbed_channels_data = []

    for chan_data in get_channels_full_data():
        if not await __check_status_is_member(bot, chan_data.get('id'), user_id):
            not_subbed_channels_data.append(chan_data)

    return Keyboards.get_not_subbed_markup(not_subbed_channels_data)


async def __check_status_is_member(bot: Bot, channel_id: int, user_id: int):
    try:
        user = await bot.get_chat_member(channel_id, user_id)
        if user.status != ChatMemberStatus.LEFT:
            return True
        return False
    except (Unauthorized, ChatNotFound, BotKicked) as e:
        logger.error(f'{e} {channel_id} при проверке обязательной подписки')
        return True
