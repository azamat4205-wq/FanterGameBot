from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import random
import os

TOKEN = os.getenv("8915110177:AAH1vTla4PHAPYy_SY22aywNB34o7UZ9YMI")

MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["🎮 Игры", "ℹ️ Помощь"]
    ],
    resize_keyboard=True
)

GAMES_MENU = ReplyKeyboardMarkup(
    [
        ["✂️ Камень Ножницы Бумага"],
        ["⭕ Крестики Нолики"],
        ["🪙 Орёл или Решка"],
        ["🎯 Русская Рулетка"],
        ["🔙 Назад"]
    ],
    resize_keyboard=True
)

KNB_MENU = ReplyKeyboardMarkup(
    [
        ["🪨 Камень", "✂️ Ножницы", "📄 Бумага"],
        ["🔙 Назад"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Добро пожаловать в FanterGameBot!",
        reply_markup=MAIN_MENU
    )

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎮 Игры":
        await update.message.reply_text(
            "Выберите игру:",
            reply_markup=GAMES_MENU
        )

    elif text == "ℹ️ Помощь":
        await update.message.reply_text(
            "👨‍💻 Поддержка:\n@azamat0158"
        )

    elif text == "🔙 Назад":
        await update.message.reply_text(
            "🏠 Главное меню",
            reply_markup=MAIN_MENU
        )

    elif text == "✂️ Камень Ножницы Бумага":
        await update.message.reply_text(
            "Выберите вариант:",
            reply_markup=KNB_MENU
        )

    elif text in ["🪨 Камень", "✂️ Ножницы", "📄 Бумага"]:

        bot_choice = random.choice(
            ["🪨 Камень", "✂️ Ножницы", "📄 Бумага"]
        )

        await update.message.reply_text(
            f"🤖 Бот выбрал:\n{bot_choice}"
        )

    elif text == "🪙 Орёл или Решка":
        result = random.choice(["🦅 Орёл", "🪙 Решка"])

        await update.message.reply_text(
            f"Результат:\n{result}"
        )

    elif text == "⭕ Крестики Нолики":
        await update.message.reply_text(
            "🚧 Крестики-нолики скоро будут добавлены."
        )

    elif text == "🎯 Русская Рулетка":
        result = random.choice(
            [
                "✅ Повезло!",
                "💥 Вы проиграли!"
            ]
        )

        await update.message.reply_text(result)

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, messages)
)

print("FanterGameBot запущен")

app.run_polling()
