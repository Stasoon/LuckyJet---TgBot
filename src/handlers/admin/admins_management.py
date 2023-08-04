from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from src.misc.admin_states import AdminAdding
from src.database.admin import add_admin, delete_admin, is_admin_exist, get_admins


admins_management_callback_data = CallbackData('admins_management', 'action')


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('👤 Управление админами 👤')

    menu_markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton('➕ Добавить админа', callback_data=admins_management_callback_data.new('add')),
        InlineKeyboardButton('➖ Исключить админа', callback_data=admins_management_callback_data.new('delete')),
        InlineKeyboardButton('📋 Список админов', callback_data=admins_management_callback_data.new('list')),
    )

    cancel_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Отменить', callback_data=admins_management_callback_data.new('cancel'))
    )


class Handlers:
    @staticmethod
    async def __handle_admin_management_button(message: Message):
        await message.answer('Что вы хотите сделать?', reply_markup=Keyboards.menu_markup)

    @staticmethod
    async def __handle_add_admin_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer('🔘 Получите id человека в боте @getmyid_bot. \n'
                                      'Затем пришлите его сюда',
                                      reply_markup=Keyboards.cancel_markup)
        await state.set_state(AdminAdding.wait_for_new_admin_id)

    @staticmethod
    async def __handle_new_admins_message(message: Message, state: FSMContext):
        if message.text.isdigit():
            await state.finish()

            if is_admin_exist(int(message.text)):
                await message.answer('❗ Этот человек уже является админом!',
                                     reply_markup=Keyboards.cancel_markup)
                return

            add_admin(telegram_id=int(message.text), admin_name='Админ')
            await message.answer('✅ Админ добавлен')

        else:
            await message.answer('❗id не может содержать букв! Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)

    @staticmethod
    async def __handle_delete_admin_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer('🔘 Пришлите мне id админа, которого хотите исключить: ',
                                      reply_markup=Keyboards.cancel_markup)
        await state.set_state(AdminAdding.wait_for_admin_to_delete_id)

    @staticmethod
    async def __handle_admin_to_delete_id(message: Message, state: FSMContext):
        if delete_admin(message.text):
            await message.answer('✅ Админ исключён!')
            await state.finish()
        else:
            await message.answer('❗Админа с таким id не существует. Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)

    @staticmethod
    async def __handle_show_admins_list_callback(callback: CallbackQuery):
        await callback.message.delete()
        text = '<b>Список добавленных администраторов бота:</b> \n\n'
        for tg_id, name in get_admins():
            text += f'<code>{tg_id}</code> — <a href="tg://user?id={tg_id}">{name}</a> \n'
        await callback.message.answer(text, reply_markup=Keyboards.cancel_markup)

    @staticmethod
    async def __handle_cancel_management_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await state.finish()
        await callback.message.answer('Что вы хотите сделать?', reply_markup=Keyboards.menu_markup)

    @classmethod
    def register_admin_management_handlers(cls, dp: Dispatcher):
        dp.register_message_handler(cls.__handle_admin_management_button,
                                    text=Keyboards.reply_button_for_admin_menu.text,
                                    is_admin=True)

        # добавление
        dp.register_callback_query_handler(cls.__handle_add_admin_callback,
                                           admins_management_callback_data.filter(action='add'),
                                           state=None)
        dp.register_message_handler(cls.__handle_new_admins_message, is_admin=True,
                                    state=AdminAdding.wait_for_new_admin_id)

        # удаление
        dp.register_callback_query_handler(cls.__handle_delete_admin_callback,
                                           admins_management_callback_data.filter(action='delete'),
                                           state=None)
        dp.register_message_handler(cls.__handle_admin_to_delete_id, is_admin=True,
                                    state=AdminAdding.wait_for_admin_to_delete_id)

        # список
        dp.register_callback_query_handler(cls.__handle_show_admins_list_callback,
                                           admins_management_callback_data.filter(action='list'))

        # отмена
        dp.register_callback_query_handler(cls.__handle_cancel_management_callback,
                                           admins_management_callback_data.filter(action='cancel'),
                                           state='*')



