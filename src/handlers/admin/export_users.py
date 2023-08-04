import os

from openpyxl import Workbook
from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message

from src.database.user import get_all_users


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('📥 Экспорт пользователей 📥')


output_filename = 'Пользователи.xlsx'


class Utils:
    @staticmethod
    async def write_users_to_xl() -> None:
        wb = Workbook()
        ws = wb.active
        ws.append(('№', 'telegram_id', 'Имя', 'Реферальная ссылка', 'Дата регистрации', 'Язык'))
        for n, user_data in enumerate(get_all_users(), 1):
            ws.append((n, *user_data))
        wb.save(output_filename)

    @staticmethod
    async def send_users_xl(to_message: Message) -> None:
        with open(output_filename, 'rb') as excel_file:
            await to_message.answer_document(document=excel_file)
        os.remove(output_filename)


class Handlers:
    @staticmethod
    async def __handle_admin_export_button(message: Message):
        await Utils.write_users_to_xl()
        await Utils.send_users_xl(message)

    @classmethod
    def register_export_users_handlers(cls, dp: Dispatcher):
        dp.register_message_handler(cls.__handle_admin_export_button, is_admin=True,
                                    text=Keyboards.reply_button_for_admin_menu.text)
