from aiogram import executor
from app import utils
from app.loader import dp

from app import middlewares, filters, handlers

async def on_startup(dp):
    await utils.on_startup_notify(dp)
    await utils.set_bot_commands(dp)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)