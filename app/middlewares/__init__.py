from app.loader import dp

from .throttling import ThrottlingMiddleware


if __name__ == 'app.middlewares':
    dp.middleware.setup(ThrottlingMiddleware())