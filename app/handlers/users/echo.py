from aiogram import types
from app.loader import dp


@dp.message_handler()
async def bot_echo(message: types.Message):
    await message.answer(message.text)