from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from app.config import admins


class Admin_fliter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        if message.from_user.id in admins:
            print('ADMIN FILTER TRUE')
            return True

def admin_filter_setup(dp):
    dp.filters_factory.bind(Admin_fliter)