from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import Regexp

from app.loader import dp


@dp.message_handler(CommandStart())
@dp.message_handler(Regexp('привет.*'))
async def bot_start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.full_name}!\nДля просмотра моих возможностей воспользуйся командой /help.')