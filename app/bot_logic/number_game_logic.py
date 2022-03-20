import random


class Number_Game:
    min_num = 1
    max_num = 1000

    def __init__(self, user):
        self.user = user
        self.user_name = None
        self.is_active = True
        self.number = round(random.uniform(1, 1000))
        self.try_cnt = 0
        self.eblan_cnt = 0

    def __repr__(self):
        return f'GAME: user = {self.user}, username = {self.user_name}, act = {self.is_active}, number = {self.number}, try = {self.try_cnt}, eblan = {self.eblan_cnt}\n'


    # DB methods
    @staticmethod
    def send_eblan_to_admin_db(user_name):
        return f'Пользователь @{user_name} еблан!'

    @staticmethod
    def more_less_equal_db(num: int, guessed_number: int):
        if num == guessed_number:
            return 1
        elif num > guessed_number:
            return 2
        else:
            return 3

    @staticmethod
    def send_end_to_admin_db(username, number, try_cnt):
        return f'Пользователь @{username} угадал число {number} за {try_cnt} попыток.'

    @staticmethod
    def send_end_by_command_db(username, try_cnt):
        return f'Пользователь @{username} прервал игру спустя {try_cnt} попыток.'

    @staticmethod
    def send_start_to_admin_db(username, number):
        return f'Пользователь @{username} начал игру.\nЕму загадано число {number}.'