import os
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("ОШИБКА: Токен не найден! Проверьте переменную BOT_TOKEN в настройках Railway.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ХРАНИЛИЩЕ СОСТОЯНИЙ (Вместо базы данных) ---
# Структура: { chat_id: { 'game': 'tictactoe', 'players': [id1, id2], 'state': {...} } }
games_state = {}

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_user_name(user):
    return user.first_name or "Игрок"

def create_keyboard(buttons, cols=2):
    """Создает клавиатуру из списка кнопок"""
    keyboard = []
    for i in range(0, len(buttons), cols):
        row = buttons[i:i + cols]
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_main_menu():
    buttons = [
        InlineKeyboardButton(text="🎮 Выбрать игру", callback_data="menu_games"),
        InlineKeyboardButton(text="👥 Пригласить друга", callback_data="invite_friend")
    ]
    return create_keyboard(buttons, cols=1)

def get_games_list():
    buttons = [
        InlineKeyboardButton(text="🪙 Орел и Решка", callback_data="game_coin"),
        InlineKeyboardButton(text="❌ Крестики-Нолики", callback_data="game_tictactoe"),
        InlineKeyboardButton(text="🎯 Найди пару (Смайлики)", callback_data="game_match"),
        InlineKeyboardButton(text="🔫 Русская рулетка", callback_data="game_roulette"),
        InlineKeyboardButton(text="🎱 4 в ряд", callback_data="game_connect4"),
        InlineKeyboardButton(text="⚡ Кто быстрее", callback_data="game_speed"),
        InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_main")
    ]
    return create_keyboard(buttons, cols=2)

def get_mode_selection():
    buttons = [
        InlineKeyboardButton(text="🤖 Играть с Ботом", callback_data="mode_bot"),
        InlineKeyboardButton(text="👥 Играть с Другом", callback_data="mode_friend"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_games")
    ]
    return create_keyboard(buttons, cols=1)

# --- ЛОГИКА ИГР ---

# 1. Орел и Решка (Coin Flip)
async def handle_coin_flip(callback, mode):
    user_id = callback.from_user.id
    bet = 10
    
    # Простая проверка баланса (в памяти)
    if user_id not in games_state:
        games_state[user_id] = {"coins": 100}
    
    if games_state[user_id].get("coins", 0) < bet:
        await callback.answer("Недостаточно монет!", show_alert=True)
        return

    result = random.choice(["heads", "tails"])
    user_choice = "heads" # Для простоты бот всегда ставит на орла, если играет с ботом, или пользователь выбирает
    
    # В режиме друга логика сложнее, пока упростим до выбора пользователя перед броском
    # Для демо: сразу показываем результат
    
    is_win = result == user_choice
    change = bet * 2 if is_win else -bet
    games_state[user_id]["coins"] += change
    
    res_emoji = "🪙" if result == "heads" else "🦅"
    outcome = "ПОБЕДА! 🎉" if is_win else "ПРОИГРЫШ 😔"
    
    text = (
        f"🪙 **Орел и Решка**\n\n"
        f"Ты поставил {bet} монет.\n"
        f"Выпало: {res_emoji} **{result.upper()}**\n"
        f"{outcome}\n"
        f"Твой баланс: {games_state[user_id]['coins']}"
    )
    
    kb = [
        InlineKeyboardButton(text="🔄 Играть снова", callback_data="game_coin"),
        InlineKeyboardButton(text="🔙 В меню игр", callback_data="back_games")
    ]
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=create_keyboard(kb, cols=2))

# 2. Крестики-Нолики (Tic-Tac-Toe)
async def handle_tictactoe(callback, mode):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    
    # Инициализация игры
    if chat_id not in games_state or games_state[chat_id].get('game') != 'tictactoe':
        games_state[chat_id] = {
            'game': 'tictactoe',
            'board': [' '] * 9,
            'current_player': user_id, # Первый ходит тот, кто начал
            'players': [user_id],
            'vs_bot': (mode == 'bot')
        }
        if mode == 'friend':
            text = (
                f"❌ **Крестики-Нолики**\n\n"
                f"Игра создана!\n"
                f"Отправь эту ссылку другу, чтобы он присоединился:\n"
                f"`t.me/{(await bot.get_me()).username}?start=join_{chat_id}`\n\n"
                f"Ждем второго игрока..."
            )
            kb = [InlineKeyboardButton(text="🔙 Отмена", callback_data="back_games")]
            await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=create_keyboard(kb))
            return

    state = games_state[chat_id]
    
    # Проверка на присоединение друга
    if mode == 'friend' and len(state['players']) < 2:
        # Логика присоединения через start параметр обрабатывается отдельно, 
        # здесь просто ждем
        pass 

    # Отрисовка доски
    b = state['board']
    board_str = (
        f"{b} | {b} | {b}\n"
        f"---------\n"
        f"{b} | {b} | {b}\n"
        f"---------\n"
        f"{b} | {b} | {b}"
    )
    
    current_name = get_user_name(callback.from_user)
    status = f"Ход: {current_name}"
    
    buttons = []
    for i in range(9):
        if b[i] == ' ':
            buttons.append(InlineKeyboardButton(text=f"{i+1}", callback_data=f"ttt_move_{i}"))
        else:
            buttons.append(InlineKeyboardButton(text=b[i], callback_data="ignore"))
    
    kb = create_keyboard(buttons, cols=3)
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Выйти из игры", callback_data="leave_game")])
    
    await callback.message.edit_text(f"❌ **Крестики-Нолики**\n\n{board_str}\n\n{status}", parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

# Обработчик хода в крестики-нолики (упрощенно)
@dp.callback_query(F.data.startswith("ttt_move_"))
async def process_ttt_move(callback):
    index = int(callback.data.split("_"))
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    
    if chat_id not in games_state or games_state[chat_id]['game'] != 'tictactoe':
        await callback.answer("Игра уже завершена или не найдена.", show_alert=True)
        return

    state = games_state[chat_id]
    
    # Проверка: твой ли это ход?
    if state['current_player'] != user_id:
        await callback.answer("Не твой ход!", show_alert=True)
        return

    if state['board'][index] != ' ':
        await callback.answer("Клетка занята!", show_alert=True)
        return

    # Делаем ход
    symbol = 'X' if user_id == state['players'] else 'O'
    state['board'][index] = symbol
    
    # Проверка победы
    win_conditions = [
        (0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)
    ]
    winner = None
    for a, b, c in win_conditions:
        if state['board'][a] == state['board'][b] == state['board'][c] != ' ':
            winner = state['board'][a]
            break
    
    if winner:
        p_name = get_user_name(callback.from_user)
        text = f"❌ **Крестики-Нолики**\n\nПОБЕДИТЕЛЬ: {p_name}! 🏆\nИгра окончена."
        await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=None)
        del games_state[chat_id]
        return

    if ' ' not in state['board']:
        text = "❌ **Крестики-Нолики**\n\nНичья! 🤝"
        await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=None)
        del games_state[chat_id]
        return

    # Смена хода
    other_id = state['players'] if len(state['players']) > 1 else state['players']
    # Простая логика смены: если есть друг, ходим к нему, иначе бот (заглушка)
    if len(state['players']) > 1 and state['players'] != user_id:
         state['current_player'] = state['players']
         await callback.message.edit_text("Ход передан сопернику...", reply_markup=None)
         # Тут нужно отправить сообщение другому игроку, но в рамках одного чата это сложно без ID второго сообщения.
         # Для демо: просто обновляем сообщение и ждем следующего нажатия (упрощение)
         await handle_tictactoe(callback, 'friend') 
    else:
        # Ход бота (случайный)
        empty_indices = [i for i, x in enumerate(state['board']) if x == ' ']
        if empty_indices:
            bot_move = random.choice(empty_indices)
            state['board'][bot_move] = 'O'
            await handle_tictactoe(callback, 'bot')

# 3. Русская рулетка (Упрощенная)
async def handle_roulette(callback, mode):
    user_id = callback.from_user.id
    if user_id not in games_state: games_state[user_id] = {"coins": 100}
    
    if games_state[user_id].get("coins", 0) < 50:
        await callback.answer("Нужно 50 монет для ставки!", show_alert=True)
        return

    # 1 из 6 шанс проиграть
    result = random.randint(1, 6)
    
    if result == 1:
        games_state[user_id]["coins"] -= 50
        text = "🔫 **Русская рулетка**\n\nБАХ! 💥 Ты проиграл 50 монет.\nТвой баланс: " + str(games_state[user_id]["coins"])
    else:
        games_state[user_id]["coins"] += 20
        text = "🔫 **Русская рулетка**\n\nЩелк! 🤞 Ты выжил и получил 20 монет!\nТвой баланс: " + str(games_state[user_id]["coins"])
        
    kb = [
        InlineKeyboardButton(text="🔄 Крутануть снова", callback_data="game_roulette"),
        InlineKeyboardButton(text="🔙 В меню", callback_data="back_games")
    ]
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=create_keyboard(kb))

# 4. Кто быстрее (Reaction Race)
async def handle_speed_game(callback, mode):
    text = (
        "⚡ **Кто быстрее?**\n\n"
        "Нажми кнопку ниже как можно быстрее!\n"
        "Таймер запустится через 3... 2... 1..."
    )
    # В реальном боте тут нужна сложная логика с таймерами и фиксацией времени нажатия.
    # Для прототипа: рандомный победитель.
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    await asyncio.sleep(2)
    
    winner_name = get_user_name(callback.from_user)
    text = f"⚡ **СТОП!**\n\n🏆 Победил: {winner_name}!\nТы самый быстрый! 😎"
    
    kb = [
        InlineKeyboardButton(text="🔄 Сыграть еще", callback_data="game_speed"),
        InlineKeyboardButton(text="🔙 В меню", callback_data="back_games")
    ]
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=create_keyboard(kb))

# Обработчик выхода из игры
@dp.callback_query(F.data == "leave_game")
async def leave_game(callback):
    chat_id = callback.message.chat.id
    user_name = get_user_name(callback.from_user)
    
    if chat_id in games_state:
        del games_state[chat_id]
        await callback.message.edit_text(f"🚪 {user_name} вышел из игры.", reply_markup=None)
        # В реальном проекте тут нужно отправить уведомление второму игроку
    else:
        await callback.answer("Ты не в игре.", show_alert=True)

# --- ОСНОВНЫЕ ОБРАБОТЧИКИ МЕНЮ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_name = message.from_user.first_name
    text = (
        f"👋 Привет, {user_name}!\n\n"
        f"Добро пожаловать в **FanterGameBot**!\n"
        f"Здесь собраны лучшие мини-игры.\n"
        f"Выбери действие:"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu())

@dp.callback_query(F.data == "back_main")
async def back_main(callback):
    await callback.message.edit_text("Главное меню:", reply_markup=get_main_menu())

@dp.callback_query(F.data == "menu_games")
async def show_games(callback):
    await callback.message.edit_text("🎮 **Выбери игру:**", parse_mode=ParseMode.MARKDOWN, reply_markup=get_games_list())

@dp.callback_query(F.data == "back_games")
async def back_games(callback):
    await callback.message.edit_text("🎮 **Выбери игру:**", parse_mode=ParseMode.MARKDOWN, reply_markup=get_games_list())

@dp.callback_query(F.data == "invite_friend")
async def invite_friend(callback):
    bot_name = (await bot.get_me()).username
    link = f"t.me/{bot_name}?start=invite"
    text = (
        f"👥 **Пригласить друга**\n\n"
        f"Отправь эту ссылку, чтобы играть вместе:\n"
        f"{link}\n\n"
        f"Или просто пришли ссылку на этот чат, если игра в группе."
    )
    kb = [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=create_keyboard(kb))

# Выбор режима игры
@dp.callback_query(F.data.startswith("game_"))
async def select_game_mode(callback):
    game_map = {
        "game_coin": ("Орел и Решка", handle_coin_flip),
        "game_tictactoe": ("Крестики-Нолики", handle_tictactoe),
        "game_roulette": ("Русская рулетка", handle_roulette),
        "game_speed": ("Кто быстрее", handle_speed_game),
        # Match и Connect4 требуют больше кода для прототипа, добавлены заглушки
        "game_match": ("Найди пару (Скоро)", lambda c, m: c.answer("Эта игра в разработке!", show_alert=True)),
        "game_connect4": ("4 в ряд (Скоро)", lambda c, m: c.answer("Эта игра в разработке!", show_alert=True)),
    }
    
    game_name, handler = game_map.get(callback.data, (None, None))
    if game_name:
        # Сохраняем имя игры во временном состоянии, чтобы передать в handler
        # Но так как handler асинхронный, проще вызвать сразу с заглушкой режима
        # Для полноценного выбора режима (бот/друг) нужно промежуточное состояние.
        # Упрощаем: сразу показываем выбор режима.
        
        # Сохраняем тип игры в контексте (упрощенно через глобальный стейт для сессии)
        # В реальном проекте лучше использовать FSM, но тут сделаем хак:
        # Мы просто передадим тип игры в callback_data следующего шага.
        
        kb = get_mode_selection()
        # Хак: сохраняем игру в стейт по chat_id временно
        if callback.message.chat.id not in games_state:
            games_state[callback.message.chat.id] = {}
        games_state[callback.message.chat.id]['pending_game'] = callback.data
        
        await callback.message.edit_text(f"🎮 **{game_name}**\nС кем хочешь сыграть?", reply_markup=kb)

# Обработка выбора режима (Бот / Друг)
@dp.callback_query(F.data.startswith("mode_"))
async def play_game(callback):
    chat_id = callback.message.chat.id
    mode = callback.data.split("_") # 'bot' or 'friend'
    
    pending = games_state.get(chat_id, {}).get('pending_game')
    if not pending:
        await callback.answer("Сначала выбери игру!", show_alert=True)
        return
    
    # Вызываем соответствующую функцию игры
    game_map = {
        "game_coin": handle_coin_flip,
        "game_tictactoe": handle_tictactoe,
        "game_roulette": handle_roulette,
        "game_speed": handle_speed_game,
    }
    
    handler = game_map.get(pending)
    if handler:
        await handler(callback, mode)
    else:
        await callback.answer("Игра временно недоступна", show_alert=True)

# Обработка deep linking (приглашение друга)
@dp.message(Command("start"))
async def cmd_start_deep(message: types.Message):
    args = message.text.split()
    if len(args) > 1:
        arg = args
        if arg.startswith("join_"):
            target_chat = arg.split("_")
            # Логика присоединения к игре в другом чате сложна для одного файла без БД.
            # Для демо: просто приветствие.
            await message.answer(f"Привет! Ты хочешь присоединиться к игре в чате {target_chat}.\nПока эта функция в разработке, но ты можешь создать свою игру!")
            return
        elif arg == "invite":
            await message.answer("Спасибо, что присоединился! Выбирай игру в меню.")
            
    # Обычный старт
    await cmd_start(message)

# --- ЗАПУСК ---
async def main():
    logger.info("Бот запущен. Доступные игры: Орел/Решка, Крестики-Нолики, Рулетка, Скорость.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен.")
        
