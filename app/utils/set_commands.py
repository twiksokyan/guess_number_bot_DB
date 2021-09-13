from aiogram import types


async def set_bot_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'начать диалог'),
            types.BotCommand('help', 'список доступных команд'),
            types.BotCommand('number_game', 'игра "Угадай число"'),
            types.BotCommand('finish_number_game', 'завершить игру')
        ]
    )