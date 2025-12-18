import os
from dotenv import load_dotenv
from aiogram import Bot


load_dotenv()

API_TOKEN = "5352353471:AAEeZ4W69c2n-25pN7BDeai-mVV16N0k8Pk"

bot = Bot(token=API_TOKEN)
ya_token = os.getenv("YA_TOKEN") 

if not API_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

admins = [1012078689, 833158284, 2072703063, 431763402, 6802387226, 470678157, 5628575737]
main_admin = 1012078689