import asyncio
from typing import Iterable
from urllib.parse import urlparse

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import RetryAfter
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from src.misc.admin_states import MailingPostCreating
from src.database.user import get_user_ids
from src.utils import logger


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('✉ Рассылка ✉')

    add_button_markup = InlineKeyboardMarkup(row_width=1) \
        .add(InlineKeyboardButton('Продолжить без кнопки', callback_data='continue_wout_button'))

    cancel_button = InlineKeyboardButton(text='🔙 Отменить', callback_data='cancel_mailing')
    cancel_markup = InlineKeyboardMarkup().add(cancel_button)

    confirm_mailing_markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton('❗ Начать рассылку ❗', callback_data='start_mailing'),
        cancel_button)

    @staticmethod
    def get_markup_from_text(text: str) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()  # По умолчанию - 1 кнопка в ряду

        # Разбиваем текст на строки и обрабатываем каждую строку
        lines = text.split('\n')
        for line in lines:
            items = line.strip().split('|')
            row_buttons = []
            for item in items:
                item_parts = item.strip().split()
                title = ' '.join(item_parts[:-1])  # Берем все слова, кроме последнего, как текст кнопки
                url = item_parts[-1]  # Последнее слово в строке считаем ссылкой
                button = InlineKeyboardButton(text=title, url=url)
                row_buttons.append(button)

            markup.row(*row_buttons)
        return markup


class Messages:
    @staticmethod
    def ask_for_post_content():
        return "Пришлите <u>текст</u> поста, который хотите разослать. Добавьте нужные <u>медиа-файлы</u>"

    @staticmethod
    def get_button_data_incorrect():
        return 'Отправленная информация не верна. ' \
               'Пожалуйста, в первой строке напишите название кнопки, во второй - ссылку.'

    @staticmethod
    def prepare_post():
        return "<i>Пост, который будет разослан:</i>"

    @staticmethod
    def get_mailing_canceled():
        return '⛔ Рассылка отменена'

    @staticmethod
    def get_markup_adding_manual():
        return '''Отправьте боту название кнопки и адрес ссылки. Например, так: 

Telegram telegram.org

Чтобы отправить несколько кнопок за раз, используйте разделитель «|». Каждый новый ряд – с новой строки. Например, так: 

Telegram telegram.org | Новости telegram.org/blog
FAQ telegram.org/faq | Скачать telegram.org/apps'''

    @staticmethod
    def ask_about_start_mailing():
        return "<u><b>Начать рассылку?</b></u>"

    @staticmethod
    def get_mailing_started():
        return "✅ <b>Рассылка началась!</b>"

    @staticmethod
    def get_successful_mailed(successful_count: int):
        return f'✅ <b>Успешно разослано {successful_count} пользователям.</b>'


class Utils:
    @classmethod
    async def send_message_to_user(cls, bot: Bot, user_id: int, from_chat_id: int, message_id: int,
                                   markup: InlineKeyboardMarkup = None) -> bool:
        try:  # пробуем скопировать сообщение с постом в чат пользователю
            await bot.copy_message(user_id, from_chat_id, message_id, reply_markup=markup)
        except RetryAfter as e:  # обрабатываем ошибку слишком частой отправки
            await asyncio.sleep(e.timeout)
            return await cls.send_message_to_user(bot, user_id, from_chat_id, message_id, markup)
        except Exception as e:
            logger.error(e)
            return False
        else:  # возвращаем True, если прошло успешно
            return True


class Mailer:
    @classmethod
    async def start_mailing(cls, bot: Bot, to_user_ids: Iterable, message_id: int, from_chat_id: int,
                            markup: InlineKeyboardMarkup = None) -> int:
        successful_count = 0
        try:
            for user_id in to_user_ids:
                if await Utils.send_message_to_user(bot, user_id, from_chat_id, message_id, markup):
                    successful_count += 1
                await asyncio.sleep(0.05)
        finally:
            logger.info(f'Рассылка закончилась, {successful_count} юзеров получили сообщения.')
            return successful_count


class Handlers:
    @staticmethod
    async def __handle_admin_mailing_button(message: Message, state: FSMContext):
        await message.answer(Messages.ask_for_post_content(),
                             reply_markup=Keyboards.cancel_markup)
        await state.set_state(MailingPostCreating.wait_for_content_message)

    @staticmethod
    async def __handle_post_content(message: Message, state: FSMContext):
        await state.update_data(message_id=message.message_id)

        await message.answer(Messages.get_markup_adding_manual(),
                             reply_markup=Keyboards.add_button_markup,
                             disable_web_page_preview=True)

        await state.set_state(MailingPostCreating.wait_for_button_data)

    @staticmethod
    async def __handle_url_button_data(message: Message, state: FSMContext):
        markup = Keyboards.get_markup_from_text(message.text)

        await message.answer(Messages.prepare_post())

        try:
            await Mailer.start_mailing(message.bot, to_user_ids=(message.from_user.id,),
                                       message_id=(await state.get_data()).get('message_id'),
                                       from_chat_id=message.from_id,
                                       markup=markup)
        except Exception as e:
            print(e)
            await message.answer('Вы ввели неправильную информацию. Попробуйте снова:',
                                 reply_markup=Keyboards.add_button_markup)
            return

        await state.update_data(markup=markup)
        await message.answer(Messages.ask_about_start_mailing(), reply_markup=Keyboards.confirm_mailing_markup)
        await state.set_state(MailingPostCreating.wait_for_confirm)

    @staticmethod
    async def __handle_continue_wout_button_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()

        await callback.message.answer(Messages.prepare_post())
        await Mailer.start_mailing(callback.message.bot, to_user_ids=(callback.from_user.id,),
                                   message_id=(await state.get_data()).get('message_id'),
                                   from_chat_id=callback.from_user.id, markup=None)

        await callback.message.answer(Messages.ask_about_start_mailing(), reply_markup=Keyboards.confirm_mailing_markup)
        await state.set_state(MailingPostCreating.wait_for_confirm)

    @staticmethod
    async def __handle_confirm_mailing_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer(Messages.get_mailing_started())

        data = await state.get_data()
        successful_count = await Mailer.start_mailing(
            bot=callback.message.bot,
            to_user_ids=get_user_ids(),
            message_id=data.get('message_id'),
            from_chat_id=callback.from_user.id,
            markup=data.get('markup')
        )

        await callback.message.answer(Messages.get_successful_mailed(successful_count))
        await state.finish()

    @staticmethod
    async def __handle_cancel_mailing_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer(Messages.get_mailing_canceled())
        await state.finish()

    @classmethod
    def register_mailing_handlers(cls, dp: Dispatcher):
        # обработка нажатия на кнопку Рассылки из меню админа
        dp.register_message_handler(cls.__handle_admin_mailing_button,
                                    is_admin=True,
                                    text=Keyboards.reply_button_for_admin_menu.text,
                                    state=None)

        # обработка контента поста
        dp.register_message_handler(cls.__handle_post_content,
                                    is_admin=True,
                                    state=MailingPostCreating.wait_for_content_message,
                                    content_types=['text', 'photo', 'video', 'animation'])

        # обработка содержимого для url-кнопки
        dp.register_message_handler(cls.__handle_url_button_data,
                                    content_types=['text'],
                                    state=MailingPostCreating.wait_for_button_data)

        # обработка калбэка продолжения без url-кнопки
        dp.register_callback_query_handler(cls.__handle_continue_wout_button_callback,
                                           state=MailingPostCreating.wait_for_button_data)

        # обработка калбэка подтверждения (начала) рассылки
        dp.register_callback_query_handler(cls.__handle_confirm_mailing_callback,
                                           is_admin=True,
                                           text='start_mailing',
                                           state=MailingPostCreating.wait_for_confirm)

        # обработка отмены рассылки
        dp.register_callback_query_handler(cls.__handle_cancel_mailing_callback,
                                           text=Keyboards.cancel_button.callback_data, state='*')
