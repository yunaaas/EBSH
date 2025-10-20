import logging
import asyncio

from aiogram import Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import bot
from users_handlers import *
from admins_handlers import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot
from config import API_TOKEN


logging.basicConfig(level=logging.INFO)




storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
bot = Bot(token=API_TOKEN)


register_user_handlers(dp)
register_admin_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)