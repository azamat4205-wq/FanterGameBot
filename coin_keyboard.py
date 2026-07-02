from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def coin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🦅 Орёл",
                    callback_data="coin_eagle"
                ),
                InlineKeyboardButton(
                    text="🪙 Решка",
                    callback_data="coin_tails"
                )
            ]
        ]
    )


def play_again_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Играть ещё раз",
                    callback_data="play_again"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
    )
