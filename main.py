import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_db
from handlers import router

bot = Bot(BOT_TOKEN)

dp = Dispatcher()


async def main():
    await init_db()

    dp.include_router(router)

    print("✅ FanterGameBot запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
