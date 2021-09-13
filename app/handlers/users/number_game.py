from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram import types

from app.loader import dp, bot

from app.keyboards.default.number_answer_kb import start_game_kb
from app.states.state_store import Number_States
from app.bot_logic.number_game_logic import Number_Game, games_dict
from app.config import admins

@dp.message_handler(Command('number_game'), state=None)
async def number_game_offer(message: types.Message):
    await message.answer(text='Я загадываю целое число от 1 до 1000.\nПопробуй его угадать!')
    await bot.send_message(chat_id=message.from_user.id, text='Играем?', reply_markup=start_game_kb)

    await Number_States.Start_game.set()


@dp.message_handler(state=Number_States.Start_game)
async def start_number_game(message: types.Message, state: FSMContext):
    m_text = message.text
    chatid = message.from_user.id

    if m_text == 'Играем!':
        games_dict[chatid] = Number_Game(chatid)
        game = games_dict[chatid]
        if message.from_user.username:
            game.user_name = message.from_user.username
        else:
            game.user_name = message.from_user.first_name + message.from_user.last_name

        await bot.send_message(chat_id=chatid, text='Я загадал число от 1 до 1000.\nПопробуй угадать. Я буду подсказывать.\n\nЕсли передумаешь продолжать играть, воспользуйся командой /finish_number_game', reply_markup=types.ReplyKeyboardRemove())

        await Number_States.Processing_game.set()

        for admin in admins:
            await bot.send_message(chat_id=admin, text=game.send_start_to_admin())
    elif m_text == 'Не буду играть':
        await bot.send_photo(chat_id=chatid, photo='https://i.ytimg.com/vi/s9Oklu-AQGQ/maxresdefault.jpg', caption='Все-го хоро-ше-го!', reply_markup=types.ReplyKeyboardRemove())

        await state.finish()
    else:
        await bot.send_message(chat_id=chatid, text='Что-нибудь попроще пожалуйста. Достаточно нажать на любую кнопку.\n\nИграем?', reply_markup=start_game_kb)


@dp.message_handler(Command('finish_number_game'), state='*')
async def finish_game_command(message: types.Message, state: FSMContext):
    chatid = message.from_user.id
    if chatid in games_dict.keys():
        game = games_dict[chatid]
        if game.is_active:
            game.is_active = False

            await message.answer(text='Игра окончена.\n\nЕсли хочешь сыграть еще раз, то снова воспользуйся командой /number_game.')

            await state.finish()

            for admin in admins:
                await bot.send_message(chat_id=admin, text=game.send_end_by_command())
        else:
            await message.answer(text='Я и так с тобой не играю сейчас.')
    else:
        await message.answer(text='Мы еще не начинали играть. Надо поближе познакомиться 😏')


@dp.message_handler(state=Number_States.Processing_game)
async def game_process(message: types.Message, state: FSMContext):
    chatid = message.from_user.id
    game = games_dict[chatid]

    try:
        user_num = int(message.text)
        if user_num > game.max_num or user_num < game.min_num:
            if game.eblan_cnt < 3:
                await bot.send_message(chat_id=chatid, text='Я загадывал число от 1 до 1000...\n\nПопробуй еще раз.')
            elif game.eblan_cnt <= 5:
                await bot.send_message(chat_id=chatid, text='Хватит издеваться...')
            else:
                await bot.send_photo(chat_id=chatid,
                                     photo='http://risovach.ru/upload/2016/04/mem/natalya-morskaya-pehota_110983292_orig_.jpg',
                                     caption='Игра окончена!')
                await state.finish()
                for admin in admins:
                    await bot.send_message(chat_id=admin, text=game.send_eblan_to_admin())
                game.is_active = False

            game.eblan_cnt += 1
        else:
            tmp = game.more_less_equal(user_num)
            if tmp == 1:
                if game.try_cnt <= 3:
                    await bot.send_photo(chat_id=chatid,
                                         photo='https://i1.sndcdn.com/artworks-000792132700-mpl9v2-t500x500.jpg',
                                         caption='Обалдеть!\nТы уже у меня в голове!')
                elif game.try_cnt <= 11:
                    await bot.send_message(chat_id=chatid, text='Правильно!\nЯ думал, ты тут надолго застрянешь!')
                else:
                    await bot.send_message(chat_id=chatid, text='Ура, наконец-то..')

                await bot.send_message(chat_id=chatid,
                                       text='Игра окончена.\n\nЕсли хочешь сыграть еще раз, то снова воспользуйся командой /number_game.')

                for admin in admins:
                    await bot.send_message(chat_id=admin, text=game.send_end_to_admin())

                game.is_active = False

                await state.finish()
            elif tmp == 2:
                await bot.send_message(chat_id=chatid, text=f'Мое число меньше, чем {user_num}')
            elif tmp == 3:
                await bot.send_message(chat_id=chatid, text=f'Мое число больше, чем {user_num}')
    except ValueError:
        if game.eblan_cnt <= 5:
            await bot.send_message(chat_id=chatid,
                                   text='Надо ввести число от 1 до 1000. Если не хочешь играть, то воспользуйся командой /finish_number_game\n\n\nИ не писай в мой горшок 😒')
        else:
            await bot.send_photo(chat_id=chatid,
                                 photo='http://risovach.ru/upload/2016/04/mem/natalya-morskaya-pehota_110983292_orig_.jpg',
                                 caption='Игра окончена!')

        game.eblan_cnt += 1