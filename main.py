from telegram import Update, ReplyKeyboardMarkup

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import TOKEN
from database import add_user, get_user

menu = ReplyKeyboardMarkup(
    [
        ["🎮 Игры", "👤 Профиль"],
        ["🎁 Кейсы", "🏆 Топ"],
        ["🎁 Ежедневный бонус", "🎟 Коды"]
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    add_user(
    update.effective_user.id,
    update.effective_user.username or update.effective_user.first_name
    )

    await update.message.reply_text(
    f"👋 Привет, {update.effective_user.first_name}!\n\n"
    "Добро пожаловать в FanterGameBot!\n"
    "Выбирай раздел ниже 👇",
    reply_markup=menu
    )

    await update.message.reply_text(
        text,
        reply_markup=menu
    )


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    print("Бот запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()
