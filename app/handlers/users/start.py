from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import Regexp

import asyncpg

from app.loader import dp, db
from app.config import admins


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    # ДЛЯ БД
    try:
        # присваиваем, потому что мы возвращаем в returning * инфу, которую заинсертили
        user = await db.add_user(
            tg_id=message.from_user.id,
            tg_username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

        user_data_dict = dict(user)

        await dp.bot.send_message(chat_id=admins[0],
                                  text='\n'.join([
                                      f'<i>Пользователь</i>',
                                      f'<code>USERNAME: {user_data_dict["tg_username"]},</code>',
                                      f'<code>TELEGRAM_ID: {user_data_dict["tg_id"]},</code>',
                                      f'<code>FULLNAME: {user_data_dict["first_name"] + " " + user_data_dict["last_name"]}</code>',
                                      '<i>добавлен в Базу.</i>'
                                  ]))
    except asyncpg.exceptions.UniqueViolationError:
        await dp.bot.send_message(chat_id=admins[0], text=f'Пользователь {message.from_user.username} : {message.from_user.id} не может быть повторно добавлен в Базу.')



    await message.answer(f'Привет, {message.from_user.full_name}!\nДля просмотра моих возможностей воспользуйся командой /help.')


@dp.message_handler(Regexp('привет.*'))
async def bot_start_hi(message: types.Message):
    await message.answer(f'Привет, {message.from_user.full_name}!\nДля просмотра моих возможностей воспользуйся командой /help.')
