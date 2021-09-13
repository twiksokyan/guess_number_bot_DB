import random


games_dict = dict()

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

    def more_less_equal(self, num: int):
        self.try_cnt += 1
        if num == self.number:
            return 1
        elif num > self.number:
            return 2
        else:
            return 3

    def send_start_to_admin(self):
        return f'Пользователь @{self.user_name} начал игру.\nЕму загадано число {self.number}.'

    def send_end_to_admin(self):
        return f'Пользователь @{self.user_name} угадал число {self.number} за {self.try_cnt} попыток.'

    def send_end_by_command(self):
        return f'Пользователь @{self.user_name} прервал игру спустя {self.try_cnt} попыток.'

    def send_eblan_to_admin(self):
        return f'Пользователь @{self.user_name} еблан!'