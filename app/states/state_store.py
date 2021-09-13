from aiogram.dispatcher.filters.state import StatesGroup, State


class Number_States(StatesGroup):
    Start_game = State()
    Processing_game = State()