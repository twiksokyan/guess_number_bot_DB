from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from app.loader import dp
from app.utils.misc import rate_limit


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = [
        'Список команд:',
        '/start - Начать диалог',
        '/help - Получить справку',
        '/number_game - Начать игру "Угадай число".\nЯ загадываю число, а ты отгадываешь',
        '/finish_number_game - Досрочно завершить игру "Угадай число".'
    ]
    await message.answer('\n\n'.join(text))