from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from src.create_bot import _


class Keyboards:
    locale_callback_data = CallbackData('locale', 'language_code')

    # region Subchecking

    check_sub_button = InlineKeyboardButton(text=_('❓ Проверить ❓'), callback_data='checksubscription')

    @classmethod
    def get_not_subbed_markup(cls, channels_to_sub_data) -> InlineKeyboardMarkup | None:
        if len(channels_to_sub_data) == 0:
            return None

        cahnnels_markup = InlineKeyboardMarkup(row_width=1)
        [
            cahnnels_markup.add(InlineKeyboardButton(channel_data.get('title'), url=channel_data.get('url')))
            for channel_data in channels_to_sub_data
        ]
        cahnnels_markup.add(cls.check_sub_button)
        return cahnnels_markup

    # endregion

    @staticmethod
    def get_locale() -> InlineKeyboardMarkup:
        russian_button = InlineKeyboardButton('Русский 🇷🇺',
                                              callback_data=Keyboards.locale_callback_data.new(language_code='ru'))
        english_button = InlineKeyboardButton('English 🇬🇧',
                                              callback_data=Keyboards.locale_callback_data.new(language_code='en'))

        return InlineKeyboardMarkup(row_width=1).add(russian_button, english_button)

    @staticmethod
    def get_welcome_menu() -> InlineKeyboardMarkup:
        start_button = InlineKeyboardButton('🚨 START 🚨', callback_data='welcome_menu')
        return InlineKeyboardMarkup(row_width=1).add(start_button)

    @staticmethod
    def get_first_signal_markup() -> InlineKeyboardMarkup:
        first_signal = InlineKeyboardButton(_('▶ ПОЛУЧИТЬ СИГНАЛ ▶'), callback_data='next_signal')
        return InlineKeyboardMarkup(row_width=2).add(first_signal)

    @staticmethod
    def get_next_signal_markup() -> InlineKeyboardMarkup:
        next_signal = InlineKeyboardButton(_('СЛЕДУЮЩИЙ РАУНД ➡'), callback_data='next_signal')
        return InlineKeyboardMarkup(row_width=2).add(next_signal)

