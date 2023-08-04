from aiogram.types import Message


async def send_typing_action(message: Message):
    await message.answer_chat_action(action='typing')
