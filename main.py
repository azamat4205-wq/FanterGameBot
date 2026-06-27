import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode

# Импорт модулей проекта
from database import Database
from keyboards import get_main_menu_keyboard, get_profile_keyboard
# Подключаем роутеры из других файлов (например, игру)
try:
    from coin_flip import router as coin_flip_router
except ImportError:
    coin_flip_router = None
    logging.warning("Файл coin_flip.py не найден или не содержит router. Функционал игры временно отключен.")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- ИНИЦИАЛИЗАЦИЯ ---

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("ОШИБКА: Токен не найден! Проверьте переменную BOT_TOKEN в настройках Railway.")

# Инициализация базы данных
try:
    db = Database()
    logger.info("База данных успешно инициализирована.")
except Exception as e:
    logger.error(f"Критическая ошибка при инициализации БД: {e}")
    raise e

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (РАБОТАЮТ С РЕАЛЬНОЙ БД) ---

async def get_user_data(user_id: int):
    """Получает данные пользователя из реальной БД"""
    try:
        # ВАЖНО: Если в database.py метод называется иначе (например, get_profile), замени здесь
        return await db.get_user(user_id)
    except Exception as e:
        logger.error(f"Ошибка получения данных пользователя {user_id}: {e}")
        return None

async def get_top_users(limit: int = 10):
    """Получает топ игроков из реальной БД"""
    try:
        # ВАЖНО: Если в database.py метод называется иначе (например, get_rating), замени здесь
        return await db.get_top(limit)
    except Exception as e:
        logger.error(f"Ошибка получения топа игроков: {e}")
        return []

# --- КЛАВИАТУРЫ (можно вынести в keyboards.py, но оставим для наглядности логики) ---

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🏆 Топ игроков", callback_data="top")],
        [InlineKeyboardButton(text="🎲 Игра: Орлянка", callback_data="game_coin_flip")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- ОБРАБОТЧИКИ (HANDLERS) ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Логика регистрации: если пользователя нет в БД, создаем его
    user_data = await get_user_data(user_id)
    if not user_data:
        try:
            await db.create_user(user_id, user_name) # Предполагаем, что такой метод есть в database.py
            logger.info(f"Новый пользователь зарегистрирован: {user_id}")
        except Exception as e:
            logger.error(f"Не удалось создать пользователя {user_id}: {e}")
            await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")
            return

    await message.answer(
        f"Привет, {user_name}! 👋\nДобро пожаловать в FanterGameBot.\nВыбери действие в меню:",
        reply_markup=get_main_menu_keyboard()
    )

@dp.callback_query(F.data == "profile")
async def show_profile(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = await get_user_data(user_id)
    
    if not user_data:
        await callback.answer("Ошибка загрузки данных профиля.", show_alert=True)
        return

    # Формируем красивое сообщение
    text = (
        f"👤 **Профиль игрока**\n\n"
        f"Имя: {user_data.get('first_name', 'Unknown')}\n"
        f"ID: <code>{user_data.get('user_id')}</code>\n"
        f"💰 Монеты: <b>{user_data.get('coins', 0)}</b>\n"
        f"📈 Уровень: {user_data.get('level', 1)}"
    )
    
    await callback.message.edit_text(
        text, 
        parse_mode=ParseMode.MARKDOWN, 
        reply_markup=get_profile_keyboard() # Используем клавиатуру из keyboards.py
    )

@dp.callback_query(F.data == "top")
async def show_top(callback: types.CallbackQuery):
    top_users = await get_top_users(5)
    
    if not top_users:
        await callback.answer("Топ игроков пока пуст.", show_alert=True)
        return

    text = "🏆 **Топ-5 игроков**\n\n"
    for i, user in enumerate(top_users, 1):
        name = user.get('first_name', 'Аноним')
        coins = user.get('coins', 0)
        text += f"{i}. {name} — {coins} монет\n"

    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data == "game_coin_flip")
async def start_game(callback: types.CallbackQuery):
    # Если роутер подключен, можно перенаправить логику туда, 
    # но для простоты пока оставим заглушку или вызов из coin_flip
    await callback.answer("Переход в игру...", show_alert=False)
    # Здесь можно вызвать логику из coin_flip.py, если она не в роутере
    await callback.message.answer("Здесь будет интерфейс игры (орлянка). Логика вынесена в coin_flip.py")

# --- ЗАПУСК ---

async def main():
    # Регистрируем роутеры из других файлов
    if coin_flip_router:
        dp.include_router(coin_flip_router)
        logger.info("Роутер coin_flip успешно подключен.")
    
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    
