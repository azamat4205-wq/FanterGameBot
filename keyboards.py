from urllib.parse import quote

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
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
            [KeyboardButton(text="🤖 Играть с ботом")],
            [KeyboardButton(text="👥 Играть с другом")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )


def games_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🪙 Орёл и решка",
                    callback_data="game_coin"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Крестики-нолики",
                    callback_data="game_ttt"
                )
            ],
            [
                InlineKeyboardButton(
                    text="😀 Найди пару",
                    callback_data="game_memory"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔫 Русская рулетка",
                    callback_data="game_rr"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔴 4 в ряд",
                    callback_data="game_connect4"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚡ Кто быстрее",
                    callback_data="game_fast"
                )
            ]
        ]
    )


def room_keyboard(link):
    share_link = (
        "https://t.me/share/url?"
        f"url={quote(link)}"
        "&text=🎮 Присоединяйся к моей игровой комнате!"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📨 Пригласить друга",
                    url=share_link
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Закрыть комнату",
                    callback_data="close_room"
                )
            ]
        ]
    )
