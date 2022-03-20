from aiogram import executor

from app import utils
from app.loader import dp, db
from app.filters.admin_filter import admin_filter_setup


from app import middlewares, filters, handlers

import logging

async def on_startup(dp):
    logging.info('Создание подключения к БД')
    # Для БД комманды, которые необходимы при запуске бота
    await db.create_connection()
    logging.info('Создание таблицы USERS')
    await db.create_table_users()
    logging.info('Создание таблицы GAMES')
    await db.create_table_games()
    logging.info('Готово!')

    await utils.on_startup_notify(dp)
    await utils.set_bot_commands(dp)

    admin_filter_setup(dp)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)