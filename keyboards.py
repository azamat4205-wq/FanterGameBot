from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🎮 Играть"),
                KeyboardButton(text="👤 Профиль")
            ],
            [
                KeyboardButton(text="🏆 Рейтинг"),
                KeyboardButton(text="📩 Помощь")
            ]
        ],
        resize_keyboard=True
    )


def play_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🤖 Играть с ботом")
            ],
            [
                KeyboardButton(text="👥 Играть с другом")
            ],
            [
                KeyboardButton(text="🔙 Назад")
            ]
        ],
        resize_keyboard=True
    )


def back_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔙 Назад")
            ]
        ],
        resize_keyboard=True
    )


def room_keyboard(room_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📨 Пригласить друга",
                    url=f"https://t.me/FanterGameBot?start=room_{room_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="cancel_room"
                )
            ]
        ]
    )
