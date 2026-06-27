import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- КОНФИГУРАЦИЯ И БЕЗОПАСНОСТЬ ---
# Токен НЕ хранится в коде. Он берётся из переменных окружения (Railway Variables).
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "ОШИБКА: Токен не найден!\n"
        "1. Зайди в настройки проекта на Railway -> Variables.\n"
        "2. Добавь переменную: Name=BOT_TOKEN, Value=твой_токен_от_botfather.\n"
        "3. Нажми Save и дождись деплоя."
    )

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (ЗАГЛУШКИ) ---
# Замени эти функции на свою реальную логику работы с базой данных.

async def get_user_data(user_id: int):
    """
    Здесь должна быть логика получения данных пользователя из БД.
    Возвращает словарь или None.
    """
    # Пример заглушки (удали это и вставь свой запрос к БД)
    return {
        "user_id": user_id,
        "first_name": "TestUser",
        "coins": 100,
        "wins": 5,
        "losses": 2
    }

async def get_top_users(limit: int):
    """
    Здесь должна быть логика получения топа игроков.
    Возвращает список словарей.
    """
    # Пример заглушки (удали это и вставь свой запрос к БД)
    return [
        {"first_name": "Alice", "coins": 500},
        {"first_name": "Bob", "coins": 450},
        {"first_name": "Charlie", "coins": 400}
    ]

# --- КЛАВИАТУРЫ ---
def get_main_menu_keyboard():
    kb = [
        [InlineKeyboardButton(text="🎮 Игры", callback_data="menu_games")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile")],
        [InlineKeyboardButton(text="🎁 Кейсы", callback_data="menu_cases")],
        [InlineKeyboardButton(text="🏆 Топ игроков", callback_data="menu_top")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_back_keyboard():
    kb = [[InlineKeyboardButton(text="🏠 Назад", callback_data="menu_main")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- ОБРАБОТЧИКИ (HANDLERS) ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Добро пожаловать в игру!\nВыбери действие в меню:",
        reply_markup=get_main_menu_keyboard()
    )

@dp.callback_query()
async def process_callback(cb: types.CallbackQuery):
    # Если нажали "Назад", возвращаем главное меню
    if cb.data == "menu_main":
        await cb.message.edit_text(
            "Главное меню:",
            reply_markup=get_main_menu_keyboard()
        )
        await cb.answer()
        return

    # --- МЕНЮ ИГР ---
    elif cb.data == "menu_games":
        await cb.message.edit_text("🎮 Выбери игру:", reply_markup=get_back_keyboard())
        await cb.answer()
        return

    # --- МЕНЮ ПРОФИЛЯ (ИСПРАВЛЕНО) ---
    elif cb.data == "menu_profile":
        # Пытаемся получить данные пользователя
        user_data = await get_user_data(cb.from_user.id)
        
        # Формируем текст безопасно, даже если данных нет
        if user_data:
            name = user_data.get('first_name', cb.from_user.first_name)
            uid = user_data.get('user_id', cb.from_user.id)
            coins = user_data.get('coins', 0)
            wins = user_data.get('wins', 0)
            losses = user_data.get('losses', 0)
        else:
            # Фоллбэк, если функция вернула None
            name = cb.from_user.first_name
            uid = cb.from_user.id
            coins, wins, losses = 0, 0, 0

        text = (
            f"👤 Профиль\n\n"
            f"Имя: {name}\n"
            f"ID: {uid}\n"
            f"Монеты: {coins}\n"
            f"Побед: {wins}\n"
            f"Поражений: {losses}"
        )
        
        await cb.message.edit_text(text, reply_markup=get_back_keyboard())
        await cb.answer()
        return

    # --- МЕНЮ КЕЙСОВ (ИСПРАВЛЕНО) ---
    elif cb.data == "menu_cases":
        text = "🎁 Кейсы — скоро можно будет открывать!"
        await cb.message.edit_text(text, reply_markup=get_back_keyboard())
        await cb.answer()
        return

    # --- МЕНЮ ТОП ИГРОКОВ (ИСПРАВЛЕНО) ---
    elif cb.data == "menu_top":
        try:
            top_players = await get_top_users(10)
            
            if not top_players:
                text = "🏆 Топ игроков пока пуст."
            else:
                lines = ["🏆 Топ игроков:\n"]
                for i, player in enumerate(top_players, 1):
                    # Адаптируй ключи ('first_name', 'coins') под свою БД
                    p_name = player.get('first_name', 'Аноним')
                    p_score = player.get('coins', player.get('score', 0))
                    lines.append(f"{i}. {p_name} — {p_score} очков")
                text = "\n".join(lines)
                
        except Exception as e:
            text = f"❌ Ошибка при загрузке топа: {e}"

        await cb.message.edit_text(text, reply_markup=get_back_keyboard())
        await cb.answer()
        return

# --- ТОЧКА ВХОДА ---
async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
