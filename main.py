import os
import random
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не найден BOT_TOKEN в .env")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Клавиатуры ---
def get_games_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎮 Камень-ножницы-бумага", callback_data="game_rps"),
        InlineKeyboardButton(text="🎲 Угадай число", callback_data="game_guess"),
    )
    builder.row(
        InlineKeyboardButton(text="❓ Квиз", callback_data="game_quiz"),
    )
    return builder.as_markup()

# --- Хендлеры ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать! Это игровой бот.\n\n"
        "Выбери игру кнопками ниже — и начнём!",
        reply_markup=get_games_keyboard(),
    )

@dp.callback_query(F.data == "game_rps")
async def game_rps(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎮 Камень-ножницы-бумага\n\n"
        "Напиши: камень, ножницы или бумага — и я сделаю свой ход."
    )
    # Здесь можно добавить логику игры (см. ниже)

@dp.callback_query(F.data == "game_guess")
async def game_guess(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎲 Угадай число от 1 до 100.\n\n"
        "Напиши число — я скажу, больше или меньше."
    )
    # Здесь можно добавить логику игры

@dp.callback_query(F.data == "game_quiz")
async def game_quiz(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "❓ Квиз\n\n"
        "Ответь на вопрос: столица Франции?"
    )
    # Здесь можно добавить логику квиза

# --- Обработка текстовых ответов (простые примеры) ---
@dp.message(F.text.lower().in_(["камень", "ножницы", "бумага"]))
async def handle_rps(message: types.Message):
    choices = ["камень", "ножницы", "бумага"]
    bot_choice = random.choice(choices)
    user = message.text.lower()

    defeats = {
        "камень": "ножницы",
        "ножницы": "бумага",
        "бумага": "камень",
    }

    if user == bot_choice:
        result = "🤝 Ничья! Я тоже выбрал(а) " + bot_choice + "."
    elif defeats[user] == bot_choice:
        result = "🎉 Ты победил! Я выбрал(а) " + bot_choice + "."
    else:
        result = "😕 Ты проиграл. Я выбрал(а) " + bot_choice + "."

    await message.answer(result)

@dp.message(F.text.isdigit())
async def handle_guess(message: types.Message):
    # Простая заглушка: в реальном боте нужно хранить состояние игры на пользователя
    number = random.randint(1, 100)
    user_num = int(message.text)

    if user_num == number:
        result = f"🎉 Угадал! Это было число {number}."
    elif user_num < number:
        result = f"📈 Больше! Ты назвал {user_num}, а число больше."
    else:
        result = f"📉 Меньше! Ты назвал {user_num}, а число меньше."

    await message.answer(result)

@dp.message(F.text.lower() == "париж")
async def handle_quiz(message: types.Message):
    await message.answer("✅ Верно! Столица Франции — Париж.")

# --- Очистка сообщений бота ---
@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    # Удаляем последние 10 сообщений бота в этом чате
    # Telegram позволяет удалять только свои сообщения и не старше 48 часов
    count = 0
    for offset in range(1, 11):
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id - offset,
            )
            count += 1
        except Exception:
            # Если сообщение не найдено или нельзя удалить — просто пропускаем
            break
    await message.answer(f"🧹 Очищено {count} сообщений бота.")

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
            
