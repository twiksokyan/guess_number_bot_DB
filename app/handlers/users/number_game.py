from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram import types

from app.loader import dp, bot, db

from app.keyboards.default.number_answer_kb import start_game_kb
from app.states.state_store import Number_States
from app.bot_logic.number_game_logic import Number_Game
from app.config import admins
from app.filters.admin_filter import Admin_fliter

@dp.message_handler(Command('number_game'), state=None)
async def number_game_offer(message: types.Message):
    await message.answer(text='Я загадываю целое число от 1 до 1000.\nПопробуй его угадать!')
    await bot.send_message(chat_id=message.from_user.id, text='Играем?', reply_markup=start_game_kb)

    await Number_States.Start_game.set()


@dp.message_handler(state=Number_States.Start_game)
async def start_number_game(message: types.Message, state: FSMContext):
    chatid = message.from_user.id

    if message.text == 'Играем!':
        # Для БД
        # Добавление пользователей, которые уже играли в меого бота
        user = await db.select_user(tg_id=chatid)
        if not user:
            await db.add_user(tg_id=message.from_user.id,
                              tg_username=message.from_user.username,
                              first_name=message.from_user.first_name,
                              last_name=message.from_user.last_name)
        # Добавление пользователей, которые уже играли в меого бота
        game = Number_Game(chatid)
        db_game = await db.add_new_game(tg_id=game.user,
                                        guessed_number=game.number)

        await bot.send_message(chat_id=chatid,
                               text='Я загадал число от 1 до 1000.\nПопробуй угадать. Я буду подсказывать.\n\nЕсли передумаешь продолжать играть, воспользуйся командой /finish_number_game',
                               reply_markup=types.ReplyKeyboardRemove())

        await Number_States.Processing_game.set()

        for admin in admins:
            await bot.send_message(chat_id=admin, text=game.send_start_to_admin_db(message.from_user.username, game.number))

            await bot.send_message(chat_id=admin,
                                   text='\n'.join([
                                       f'<i>Игра</i>',
                                       f'<code>game_id = {db_game.get("game_id")}</code>',
                                       f'<i>для пользователя</i> <code>{db_game.get("tg_id")}</code>',
                                       f'<i>добавлена в таблицу</i> <code>GAMES</code>.'
                                   ]))
    elif message.text == 'Не буду играть':
        await bot.send_photo(chat_id=chatid, photo='https://i.ytimg.com/vi/s9Oklu-AQGQ/maxresdefault.jpg', caption='Все-го хоро-ше-го!', reply_markup=types.ReplyKeyboardRemove())

        await state.finish()
    else:
        await bot.send_message(chat_id=chatid, text='Что-нибудь попроще пожалуйста. Достаточно нажать на любую кнопку.\n\nИграем?', reply_markup=start_game_kb)


@dp.message_handler(Command('finish_number_game'), state='*')
async def finish_game_command(message: types.Message, state: FSMContext):
    # Для БД
    game_id = await db.get_max_game_id(tg_id=message.from_user.id)
    if game_id:
        game = await db.select_game(game_id)
        if game.get("is_active_flg"):
            await db.update_game_break(game_id=game_id)
            await message.answer(
                text='Игра окончена.\n\nЕсли хочешь сыграть еще раз, то снова воспользуйся командой /number_game.')

            await state.finish()

            for admin in admins:
                await bot.send_message(chat_id=admin,
                                       text=Number_Game.send_end_by_command_db(message.from_user.username,
                                                                               game.get('tries_cnt')))
        else:
            await message.answer(text='Я и так с тобой не играю сейчас.')
    else:
        await message.answer(text='Мы еще не начинали играть. Надо поближе познакомиться 😏')

@dp.message_handler(state=Number_States.Processing_game)
async def game_process(message: types.Message, state: FSMContext):
    # Достаем данные из БД
    game_id = await db.get_max_game_id(tg_id=message.from_user.id)
    game_db = await db.select_game(game_id=game_id)
    game = dict(game_db)

    tg_id = game['tg_id']
    tries_cnt = game['tries_cnt']
    guessed_number = game['guessed_number']
    eblan_cnt = game['eblan_cnt']

    user = await db.get_user_from_game(game_id=game_id)

    max_num = Number_Game.max_num
    min_num = Number_Game.min_num

    # стратегия игры
    if game['is_active_flg']:
        try:
            user_num = int(message.text)
            if user_num > max_num or user_num < min_num:
                if eblan_cnt < 3:
                    await bot.send_message(chat_id=tg_id, text='Я загадывал число от 1 до 1000...\n\nПопробуй еще раз.')
                elif eblan_cnt <= 5:
                    await bot.send_message(chat_id=tg_id, text='Ты че?!')
                else:
                    await bot.send_photo(chat_id=tg_id,
                                         photo='http://risovach.ru/upload/2016/04/mem/natalya-morskaya-pehota_110983292_orig_.jpg',
                                         caption='Игра окончена!')
                    await state.finish()

                    # Admins INFO
                    for admin in admins:
                        await bot.send_message(chat_id=admin, text=Number_Game.send_eblan_to_admin_db(user.get('tg_username')))

                    # DB update
                    await db.update_game_break(game_id=game_id)

                eblan_cnt += 1
                # DB update
                await db.update_game(game_id, eblan_cnt=eblan_cnt)
            else:
                tmp = Number_Game.more_less_equal_db(user_num, guessed_number)
                if tmp == 1:
                    if tries_cnt <= 3:
                        await bot.send_photo(chat_id=tg_id,
                                             photo='https://i1.sndcdn.com/artworks-000792132700-mpl9v2-t500x500.jpg',
                                             caption='Обалдеть!\nТы уже у меня в голове!')
                    elif tries_cnt <= 11:
                        await bot.send_message(chat_id=tg_id, text='Правильно!\nЯ думал, ты тут надолго застрянешь!')
                    else:
                        await bot.send_message(chat_id=tg_id, text='Ура, наконец-то..')

                    await bot.send_message(chat_id=tg_id,
                                           text=f'Игра окончена.\n\n'
                                                f'Ты угадал число {guessed_number} с {tries_cnt + 1}-го раза.\n\n'
                                                'Если хочешь сыграть еще раз, то снова воспользуйся командой /number_game.')

                    for admin in admins:
                        await bot.send_message(chat_id=admin, text=Number_Game.send_end_to_admin_db(username=user.get('tg_username'),
                                                                                                    number=guessed_number,
                                                                                                    try_cnt=tries_cnt+1))
                    # DB update
                    await db.update_game_win(game_id=game_id)

                    await state.finish()
                elif tmp == 2:
                    await bot.send_message(chat_id=tg_id, text=f'Мое число меньше, чем {user_num}')
                elif tmp == 3:
                    await bot.send_message(chat_id=tg_id, text=f'Мое число больше, чем {user_num}')

                tries_cnt += 1
                # DB update
                await db.update_game(game_id, tries_cnt=tries_cnt)
        except ValueError:
            if eblan_cnt <= 5:
                await bot.send_message(chat_id=tg_id,
                                       text='Надо ввести число от 1 до 1000. Если не хочешь играть, то воспользуйся командой /finish_number_game')
            else:
                await bot.send_photo(chat_id=tg_id,
                                     photo='http://risovach.ru/upload/2016/04/mem/natalya-morskaya-pehota_110983292_orig_.jpg',
                                     caption='Игра окончена!')

                await state.finish()
                # DB update
                await db.update_game_break(game_id=game_id)

            eblan_cnt += 1
            # DB update
            await db.update_game(game_id, eblan_cnt=eblan_cnt)

@dp.message_handler(Command('for_admin'), Admin_fliter())
async def test_admin_command(message: types.Message):
    await message.answer(text='Ты выполнил команду для админов!')