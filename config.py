import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден!")

if not BOT_USERNAME:
    raise ValueError("BOT_USERNAME не найден!")
BOT_LINK = f"https://t.me/{BOT_USERNAME}"
