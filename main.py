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
    
app.add_handler(MessageHandler(filters.Regex("^👤 Профиль$"), profile))
    
    print("Бот запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if not user:
        await update.message.reply_text("❌ Профиль не найден.")
        return

    text = f"""
👤 <b>ПРОФИЛЬ</b>

🆔 ID: {user[0]}
📛 Имя: {user[1]}

💰 Монеты: {user[2]}
🏆 Победы: {user[3]}
❌ Поражения: {user[4]}

🎁 Кейсов: 0
🖼 Рамка: Нет
"""

    await update.message.reply_text(text, parse_mode="HTML")
