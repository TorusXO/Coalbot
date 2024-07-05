from aiogram import Dispatcher
import logging
import asyncio

from app.variables import db
from app.handlers import router
from bot_logger import bot

dp = Dispatcher()

db.create_tables()

async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(filename='bot.log', level=logging.INFO)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print ("interrupted")