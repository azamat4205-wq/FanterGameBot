from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu():
    kb = ReplyKeyboardBuilder()

    kb.button(text="🎮 Играть")
    kb.button(text="👤 Профиль")
    kb.button(text="🏆 Рейтинг")
    kb.button(text="📩 Помощь")

    kb.adjust(2, 2)

    return kb.as_markup(resize_keyboard=True)


def play_menu():
    kb = ReplyKeyboardBuilder()

    kb.button(text="🤖 Играть с ботом")
    kb.button(text="👥 Играть с другом")
    kb.button(text="🔙 Назад")

    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True)
