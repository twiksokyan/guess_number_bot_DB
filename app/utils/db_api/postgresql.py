from typing import Union

import asyncpg

from app import config

class Database:

    def __init__(self): # не очень понял, зачем это
        self.pool: Union[asyncpg.pool.Pool, None] = None

    async def create_connection(self): # функция для создания подключения к БД
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool= False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: asyncpg.Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)

            return result

    async def create_table_users(self):
        query = '''
        CREATE TABLE IF NOT EXISTS USERS (
        TG_ID BIGINT NOT NULL,
        TG_USERNAME VARCHAR(255),
        FIRST_NAME VARCHAR(255),
        LAST_NAME VARCHAR(255),
        ADDED_DT TIMESTAMP DEFAULT DATE_TRUNC('second', localtimestamp),
        PRIMARY KEY (TG_ID)
        );
        '''

        await self.execute(query, execute=True)

    async def create_table_games(self):
        query = '''
        CREATE TABLE IF NOT EXISTS GAMES (
        GAME_ID SERIAL PRIMARY KEY,
        TG_ID BIGINT NOT NULL,
        IS_ACTIVE_FLG BOOLEAN DEFAULT TRUE,
        GUESSED_NUMBER INTEGER NOT NULL,
        TRIES_CNT INTEGER DEFAULT 0,
        GUESSED_FLG BOOLEAN DEFAULT FALSE,
        BREAK_FLG BOOLEAN DEFAULT FALSE,
        EBLAN_CNT INTEGER DEFAULT 0,
        GAME_START_DTTM TIMESTAMP DEFAULT DATE_TRUNC('second', localtimestamp),
        GAME_END_DTTM TIMESTAMP,
        FOREIGN KEY (TG_ID) REFERENCES users (TG_ID)
        );
        '''

        await self.execute(query, execute=True)

    @staticmethod
    def format_args(sql, concat_var, parameters: dict): # для подстановки параметров в *args метода execute
        sql += f' {concat_var} '.join([f'{item} = ${num}' for num, item in enumerate(parameters.keys(), start=1)])

        return sql, tuple(parameters.values())

    async def add_user(self, tg_id, tg_username, first_name, last_name):
        query = '''
        INSERT INTO USERS (TG_ID, TG_USERNAME, FIRST_NAME, LAST_NAME)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        '''
        # returning * выведет запрос типа select * from user where ... про добавленного чувака после инсерта

        return await self.execute(query, tg_id, tg_username, first_name, last_name, fetchrow=True)

    # ДЛЯ ПРИМЕРА ИСПОЛЬЗОВАНИЯ МЕТОДА ВЫШЕ
    async def select_user(self, **kwargs):
        sql = 'SELECT * FROM USERS WHERE '
        sql, parameters = self.format_args(sql, 'AND', parameters=kwargs)

        return await self.execute(sql, *parameters, fetchrow=True)

    # ПРИМЕР ПОДСТАНОВКИ ПОСЛЕДОВАТЕЛЬНЫХ АРГУМЕНТОВ В *args метода execute
    async def update_user_username(self, new_username, tg_id):
        query = 'UPDATE USERS SET USERNAME = $1 WHERE TG_ID = $2'
        # агрументы прописываем в нужной последовательности НЕменованными
        return await self.execute(query, new_username, tg_id, execute=True)


    # Команды для работы с таблицей GAMES
    async def add_new_game(self, tg_id, guessed_number):
        query = '''
        INSERT INTO GAMES (TG_ID, GUESSED_NUMBER)
        VALUES ($1, $2)
        RETURNING *
        '''

        return await self.execute(query, tg_id, guessed_number, fetchrow=True)

    async def get_max_game_id(self, tg_id):
        query = '''
        SELECT MAX(GAME_ID) FROM GAMES WHERE TG_ID = $1
        '''

        return await self.execute(query, tg_id, fetchval=True)

    async def update_game_win(self, game_id, **kwargs):
        query = '''
        UPDATE GAMES
        SET IS_ACTIVE_FLG = FALSE,
            GUESSED_FLG = TRUE,
            GAME_END_DTTM = DATE_TRUNC('second', localtimestamp)
        WHERE GAME_ID = $1
        '''

        await self.execute(query, game_id, execute=True)

    async def update_game_break(self, game_id, **kwargs):
        query = '''
        UPDATE GAMES
        SET IS_ACTIVE_FLG = FALSE,
            BREAK_FLG = TRUE,
            GAME_END_DTTM = DATE_TRUNC('second', localtimestamp)
        WHERE GAME_ID = $1
        '''

        await self.execute(query, game_id, execute=True)

    async def update_game(self, game_id, **kwargs):
        query = '''
        UPDATE GAMES
        SET GAME_END_DTTM = DATE_TRUNC('second', localtimestamp), 
        '''
        query, parameters = self.format_args(query, ',', kwargs)
        query += f'\nWHERE GAME_ID = {game_id}'

        await self.execute(query, *parameters, execute=True)


    async def select_game(self, game_id):
        query = '''
        SELECT * FROM GAMES WHERE GAME_ID = $1
        '''

        return await self.execute(query, game_id, fetchrow=True)

    async def get_user_from_game(self, game_id):
        query = '''
        SELECT U.*
        FROM GAMES g
        JOIN USERS u
            ON g.TG_ID = u.TG_ID
        WHERE g.GAME_ID = $1
        '''

        return await self.execute(query, game_id, fetchrow=True)