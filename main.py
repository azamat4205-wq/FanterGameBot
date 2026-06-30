import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN
from database import init_db, add_user, get_user, get_top
from keyboards import main_menu, play_menu

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await add_user(message.from_user)

    text = (
        f"🎉 Добро пожаловать, {message.from_user.first_name}!\n\n"
        "🎮 Добро пожаловать в FanterGameBot!\n\n"
        "Выберите действие ниже 👇"
    )

    await message.answer(text, reply_markup=main_menu())


@dp.message(F.text == "🎮 Играть")
async def play(message: Message):
    await message.answer(
        "🎮 Выберите режим игры:",
        reply_markup=play_menu()
    )


@dp.message(F.text == "🔙 Назад")
async def back(message: Message):
    await message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )


@dp.message(F.text == "👤 Профиль")
async def profile(message: Message):
    user = await get_user(message.from_user.id)

    text = (
        f"👤 {user[2]}\n\n"
        f"🏆 Побед: {user[3]}\n"
        f"💀 Поражений: {user[4]}\n"
        f"🎮 Всего игр: {user[5]}"
    )

    await message.answer(text)


@dp.message(F.text == "🏆 Рейтинг")
async def rating(message: Message):
    top = await get_top()

    text = "🏆 Топ игроков\n\n"

    for i, player in enumerate(top, start=1):
        text += f"{i}. {player[0]} — {player[1]} побед\n"

    await message.answer(text)


@dp.message(F.text == "📩 Помощь")
async def help_menu(message: Message):
    await message.answer(
        "📩 По всем вопросам:\n\n@azamat0158"
    )


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
