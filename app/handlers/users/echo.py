from aiogram import types
from aiogram.dispatcher.filters import Text, Regexp

from app.loader import dp, bot


@dp.message_handler(Text(equals=['похуй'], ignore_case=True))
async def pashalochka(message: types.Message):
    await bot.send_sticker(chat_id=message.from_user.id, sticker="CAACAgIAAxkBAAELqtNhOPl1XxXI8yp8ifYWrO_UHdvYZwACawEAAg-VRRAaVsHnukWo2yAE")


@dp.message_handler(Regexp('.*хуй.*|.*[её]б.*|.*пизд.*|пидр.*|пидор|пидар.*|блять'))
async def pashalochka(message: types.Message):
    await bot.send_sticker(chat_id=message.from_user.id, sticker="CAACAgIAAxkBAAELqtFhOPgnSoA-_VozDy73DJdpwLgHbwACbwEAAg-VRRAH81MT6PA2-SAE")


@dp.message_handler()
async def bot_echo(message: types.Message):
    await message.answer('Даже не знаю, что тебе ответить...')


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def bot_photo(photo: types.Message):
    print(photo)