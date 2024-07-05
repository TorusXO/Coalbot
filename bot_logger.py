import logging
from aiogram import Bot
from config import TOKEN
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
logger = logging.getLogger()

