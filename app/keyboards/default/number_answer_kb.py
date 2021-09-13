from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


start_game_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Играем!')
        ],
        [
            KeyboardButton(text='Не буду играть')
        ]
    ],
    resize_keyboard=True
)