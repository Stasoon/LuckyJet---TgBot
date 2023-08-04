import asyncio
import random

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from src.database.user import create_user, set_locale, get_locale, set_user_1win_id, get_user_1win_id
from src.utils import send_typing_action, throttle
from src.misc import UserDataInputting
from .messages import Messages
from .kb import Keyboards
from config import CODE_WORD


async def edit_to_new_signal(to_message: Message, user_id: int):
    onewin_id = get_user_1win_id(user_id)
    new_text = Messages.get_next_signal(onewin_id)
    if to_message.text == new_text:
        await edit_to_new_signal(to_message, user_id)

    msg = await to_message.answer('1️⃣2️⃣3️⃣')
    delay_seconds = 0.4

    for i in range(1, random.randint(2, 4+1)):
        await asyncio.sleep(delay_seconds)
        await msg.edit_text('1️⃣')
        await asyncio.sleep(delay_seconds)
        await msg.edit_text('1️⃣2️⃣')
        await asyncio.sleep(delay_seconds)
        await msg.edit_text('1️⃣2️⃣3️⃣')

    await msg.edit_text(new_text, reply_markup=Keyboards.get_next_signal_markup())


# region Handlers

@throttle()
async def __handle_start_command(message: Message) -> None:
    await send_typing_action(message)
    create_user(telegram_id=message.from_id,
                name=message.from_user.username or message.from_user.full_name,
                reflink=message.get_full_command()[1])

    await message.answer_sticker(sticker=Messages.get_start_sticker())
    await message.answer(text=Messages.ask_for_locale(), reply_markup=Keyboards.get_locale())


async def __handle_locale_callback(callback: CallbackQuery, callback_data: Keyboards.locale_callback_data):
    await send_typing_action(callback.message)
    await callback.message.delete()

    language_code = callback_data.get('language_code')
    set_locale(callback.from_user.id, language_code)

    if language_code == 'ru':
        await callback.message.answer_photo(
            photo=Messages.get_welcome_photo(),
            caption=Messages.get_ru_welcome(callback.from_user.first_name),
            reply_markup=Keyboards.get_welcome_menu()
        )
    else:
        await callback.message.answer_photo(
            photo=Messages.get_welcome_photo(),
            caption=Messages.get_en_welcome(callback.from_user.first_name),
            reply_markup=Keyboards.get_welcome_menu()
        )


@throttle(rate=1.5)
async def __handle_start_callback(callback: CallbackQuery, state: FSMContext):
    await send_typing_action(callback.message)
    await callback.answer()
    await callback.message.answer(Messages.ask_for_code_word())
    await state.set_state(await UserDataInputting.first())


async def __handle_user_password_message(message: Message, state: FSMContext):
    await send_typing_action(message)
    if message.text == CODE_WORD:
        await message.answer(Messages.ask_for_1win_id())
        await state.set_state(await UserDataInputting.next())
    else:
        await message.answer(Messages.get_code_word_incorrect())


async def __handle_user_id_message(message: Message, state: FSMContext):
    await send_typing_action(message)

    if not message.text.isdigit():
        await message.answer(Messages.get_1win_id_incorrect_length())
        return
    if len(message.text) != 8:
        await message.answer(Messages.get_1win_id_have_forbidden_symbols())
        return

    set_user_1win_id(message.from_user.id, message.text)
    if get_locale(message.from_user.id) == 'ru':
        await message.answer_photo(
            photo=Messages.get_before_start_photo(),
            caption=Messages.get_before_game_start(),
            reply_markup=Keyboards.get_first_signal_markup()
        )
    else:
        await message.answer(
            text=Messages.get_before_game_start(),
            reply_markup=Keyboards.get_first_signal_markup()
        )
    await state.finish()


async def __handle_next_signal_callback(callback: CallbackQuery):
    await send_typing_action(callback.message)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await edit_to_new_signal(callback.message, callback.from_user.id)

# endregion


def register_user_handlers(dp: Dispatcher) -> None:
    # обработка команды /start
    dp.register_message_handler(__handle_start_command, commands=['start'])

    # выбор языка
    dp.register_callback_query_handler(__handle_locale_callback, Keyboards.locale_callback_data.filter())

    # обработка кнопок приветственного меню
    dp.register_callback_query_handler(__handle_start_callback, text='welcome_menu', state=None)
    dp.register_message_handler(__handle_user_id_message, state=UserDataInputting.wait_for_id)
    dp.register_message_handler(__handle_user_password_message, state=UserDataInputting.wait_for_password)

    # обработка нажатия на Следующий сигнал
    dp.register_callback_query_handler(__handle_next_signal_callback, text='next_signal')
