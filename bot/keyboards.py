from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    kb = [
        [InlineKeyboardButton(text="���ры", callback_data="menu_games")],
        [InlineKeyboardButton(text="���офиль", callback_data="menu_profile")],
        [InlineKeyboardButton(text="🎁 Кейсы", callback_data="menu_cases")],
        [InlineKeyboardButton(text="🏆 Топ игроков", callback_data="menu_top")],
        [InlineKeyboardButton(text="���едневный бонус", callback_data="menu_bonus")],
        [InlineKeyboardButton(text="���ды", callback_data="menu_codes")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def games_menu():
    kb = [
        [InlineKeyboardButton(text="���ёл и решка", callback_data="game_coin_flip")],
        [InlineKeyboardButton(text="�� Крестики‑нолики", callback_data="game_tic_tac_toe")],
        [InlineKeyboardButton(text="���сская рулетка", callback_data="game_roulette")],
        [InlineKeyboardButton(text="🔴 Четыре в ряд", callback_data="game_connect_four")],
        [InlineKeyboardButton(text="⚡ Кто быстрее", callback_data="game_quick_click")],
        [InlineKeyboardButton(text="���йди пару", callback_data="game_memory")],
        [InlineKeyboardButton(text="🏠 Назад", callback_data="menu_home")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def after_game(winner_name: str | None):
    if winner_name:
        kb = [
            [InlineKeyboardButton(text=f"🏆 Победитель: {winner_name}", callback_data="none")],
            [InlineKeyboardButton(text="���рать снова", callback_data="game_play_again")],
            [InlineKeyboardButton(text="❌ Выйти", callback_data="game_exit")],
        ]
    else:
        kb = [
            [InlineKeyboardButton(text="���рать снова", callback_data="game_play_again")],
            [InlineKeyboardButton(text="❌ Выйти", callback_data="game_exit")],
        ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
  
