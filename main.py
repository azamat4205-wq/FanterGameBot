from telegram import (
    Update,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import TOKEN
from database import add_user, get_user

menu = ReplyKeyboardMarkup(
    [
        ["🎮 Игры"],
        ["👤 Профиль", "🎒 Инвентарь"],
        ["📦 Кейсы", "🏆 Топ"],
        ["🎁 Ежедневный бонус"],
        ["🎟️ Коды", "❓ Помощь"]
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    register(update.effective_user)

    text = f"""
❤️🖤 Добро пожаловать в FanterGameBot!

🎮 Здесь тебя ждут:
• Мини-игры
• Кейсы
• Рамки
• Монеты
• Топ игроков

🔥 Желаем удачи!

Выбери раздел ниже 👇
"""

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
