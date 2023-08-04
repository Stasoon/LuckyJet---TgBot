from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from src.misc.admin_states import ReferralLinkStates
from src.database.reflink import create_reflink, is_reflink_exists, get_link_names, get_link, delete_reflink
from config import Config


reflinks_callback_data = CallbackData('referral_links', 'action')


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('🔗 Реферальные ссылки 🔗')
    reflinks_markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton('➕ Добавить ссылку', callback_data=reflinks_callback_data.new('create')),
        InlineKeyboardButton('➖ Удалить ссылку', callback_data=reflinks_callback_data.new('delete')),
        InlineKeyboardButton('📋 Список ссылок', callback_data=reflinks_callback_data.new('list')),
        InlineKeyboardButton('🔎 Найти ссылку', callback_data=reflinks_callback_data.new('find'))
    )

    cancel_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Отменить', callback_data=reflinks_callback_data.new('cancel'))
    )


class Handlers:
    @staticmethod
    async def __handle_admin_reflinks_button(message: Message):
        await message.answer('Что вы хотите сделать?', reply_markup=Keyboards.reflinks_markup)

    @staticmethod
    async def __handle_add_link_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer('🔘 Введите название. Можно использовать цифры и английские буквы:',
                                      reply_markup=Keyboards.cancel_markup)
        await state.set_state(ReferralLinkStates.create)

    @staticmethod
    async def __handle_new_link_name(message: Message, state: FSMContext):
        if not message.text.isascii():
            await message.answer('❗В сообщении есть русские буквы. Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)
        elif not message.text.isalnum():
            await message.answer('❗В сообщении есть символы. Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)
        elif is_reflink_exists(message.text):
            await message.answer('❗Такая ссылка уже существует. Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)
        else:
            create_reflink(message.text)
            await message.answer('✅ Реферальная ссылка создана. \n\n'
                                 f'<u><i>Имя ссылки</i></u>: <code>{message.text}</code> \n'
                                 f'<u><i>Ссылка</i></u>: <code>https://t.me/{Config.get_bot_username()}?start={message.text}</code>')
            await state.finish()

    @staticmethod
    async def __handle_delete_link_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer('🔘 Введите название ссылки, которую хотите удалить. ',
                                      reply_markup=Keyboards.cancel_markup)
        await state.set_state(ReferralLinkStates.delete)

    @staticmethod
    async def __handle_link_to_delete_name(message: Message, state: FSMContext):
        if not is_reflink_exists(message.text):
            await message.answer('❗Такой ссылки нет. Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)
        else:
            delete_reflink(message.text)
            await message.answer('✅ Ссылка удалена')
            await state.finish()

    @staticmethod
    async def __handle_links_list(callback: CallbackQuery):
        text = '<b>Список реферальных ссылок:</b> \n\n'
        for n, name in enumerate(get_link_names(), 1):
            text += f'{n} — <code>{name}</code> \n'
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=Keyboards.cancel_markup)

    @staticmethod
    async def __handle_find_link_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer('🔎 Введите название ссылки:', reply_markup=Keyboards.cancel_markup)
        await state.set_state(ReferralLinkStates.find)

    @staticmethod
    async def __handle_link_to_find_name(message: Message, state: FSMContext):
        link_data = get_link(message.text)
        if not get_link(message.text):
            await message.answer('❗Введённая ссылка не существует. Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)
            return

        text = f'<b>Данные реферальной ссылки</b> \n\n' \
               f'Название ссылки: {link_data[0]} \n' \
               f'Ссылка: <code>https://t.me/{Config.get_bot_username()}?start={link_data[0]}</code> \n' \
               f'📊 Кол-во переходов: {link_data[1]} \n' \
               f'На ОП подписались: {link_data[2]}'
        await message.answer(text, reply_markup=Keyboards.cancel_markup)
        await state.finish()

    @staticmethod
    async def __handle_cancel_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer('Что вы хотите сделать?', reply_markup=Keyboards.reflinks_markup)
        await state.finish()

    @classmethod
    def register_reflinks_handlers(cls, dp: Dispatcher):
        dp.register_message_handler(cls.__handle_admin_reflinks_button, is_admin=True,
                                    text=Keyboards.reply_button_for_admin_menu.text)

        # создание реферальной ссылки
        dp.register_callback_query_handler(cls.__handle_add_link_callback,
                                           reflinks_callback_data.filter(action='create'),
                                           is_admin=True, state=None)
        dp.register_message_handler(cls.__handle_new_link_name, is_admin=True, state=ReferralLinkStates.create)

        # удаление реферальной ссылки
        dp.register_callback_query_handler(cls.__handle_delete_link_callback,
                                           reflinks_callback_data.filter(action='delete'), state=None)
        dp.register_message_handler(cls.__handle_link_to_delete_name, state=ReferralLinkStates.delete)

        # показ списка ссылок
        dp.register_callback_query_handler(cls.__handle_links_list, reflinks_callback_data.filter(action='list'))

        # получение ссылки
        dp.register_callback_query_handler(cls.__handle_find_link_callback,
                                           reflinks_callback_data.filter(action='find'), state=None)
        dp.register_message_handler(cls.__handle_link_to_find_name, state=ReferralLinkStates.find)

        # отмена
        dp.register_callback_query_handler(cls.__handle_cancel_callback, reflinks_callback_data.filter(action='cancel'),
                                           state='*')

