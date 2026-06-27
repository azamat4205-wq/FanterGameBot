import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PORT, ADMIN_IDS
from database import init_db, get_or_create_user, check_daily_bonus, get_top_users, redeem_code, create_code
from keyboards import main_menu, games_menu, after_game
import coin_flip
# сюда позже можно будет добавить другие игры, если допишешь их логику

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

# --- Инициализация БД при старте ---
@dp.startup()
async def on_startup():
    await init_db()
    logging.info("База данных инициализирована.")

# --- Команда /start: приветствие и главное меню ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username or "Аноним")
    text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Твой баланс: {user['coins']} монет\n"
        f"Побед: {user['wins']} | Поражений: {user['losses']}\n\n"
        "Выбирай, что хочешь сделать:"
    )
    await message.answer(text, reply_markup=main_menu())

# --- Обработчик главного меню ---
@dp.callback_query(lambda cb: cb.data.startswith("menu_"))
async def handle_main_menu(cb: types.CallbackQuery):
    user = await get_or_create_user(cb.from_user.id, cb.from_user.username or "Аноним")

    if cb.data == "menu_home":
        text = (
            f"🏠 Главное меню\n"
            f"Баланс: {user['coins']} монет\n"
            f"Побед: {user['wins']} | Поражений: {user['losses']}"
        )
        await cb.message.edit_text(text, reply_markup=main_menu())
        await cb.answer()
        return

    elif cb.data == "menu_games":
        await cb.message.edit_text("���бери игру:", reply_markup=games_menu())
        await cb.answer()
        return

    elif cb.data == "menu_profile":
        text = (
            f"���офиль\n\n"
            f"Имя: {cb.from_user.first_name}\n"
            f"ID: {user['user_id']}\n"
            f"Монеты: {user['coins']}\n"
            f"Побед: {user['wins']}\n"
            f"Поражений: {user['losses']}"
        )
        # тут можно позже добавить красивый вывод инвентаря
        await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Назад", callback_data="menu_home")]
        ]))
        await cb.answer()
        return

    elif cb.data == "menu_cases":
        text = "🎁 Кейсы — скоро можно будет открывать! Пока тут пусто."
        await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Назад", callback_data="menu_home")]
        ]))
        await cb.answer()
        return

    elif cb.data == "menu_top":
        top = await get_top_users(10)
        if not top:
            text = "🏆 Топ игроков пока пуст."
        else:
            lines = ["🏆 Топ игроков:\n"]
            for i, u in enumerate(top, 1):
                name = u["username"] or "Аноним"
                lines.append(f"{i}. {name} — {u['coins']} монет ({u['wins']} побед)")
            text = "\n".join(lines)
        await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Назад", callback_data="menu_home")]
        ]))
        await cb.answer()
        return

    elif cb.data == "menu_bonus":
        got, amount = await check_daily_bonus(cb.from_user.id)
        if got:
            await cb.message.edit_text(f"☀️ Ежедневный бонус: +{amount} монет! 🎉", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Назад", callback_data="menu_home")]
            ]))
        else:
            await cb.message.edit_text("☀️ Ты уже забирал ежедневный бонус сегодня. Попробуй завтра!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Назад", callback_data="menu_home")]
            ]))
        await cb.answer()
        return

    elif cb.data == "menu_codes":
        # простая форма: админ может создать код, остальные — активировать
        kb = [
            [InlineKeyboardButton(text="Активировать код", callback_data="code_activate")],
        ]
        if cb.from_user.id in ADMIN_IDS:
            kb.append([InlineKeyboardButton(text="���здать код", callback_data="code_create")])
        kb.append([InlineKeyboardButton(text="🏠 Назад", callback_data="menu_home")])

        await cb.message.edit_text("���ды", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        await cb.answer()
        return

# --- Обработка активации кода ---
@dp.callback_query(lambda cb: cb.data == "code_activate")
async def code_activate_start(cb: types.CallbackQuery):
    await cb.message.edit_text("Введи код в чат (только текст, без команд):", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Отмена", callback_data="menu_home")]
    ]))
    # в полноценной версии тут лучше использовать FSM (машина состояний), чтобы ждать ответ
    # для простоты пока просто скажем: напиши код текстом
    await cb.answer()

@dp.message()
async def handle_text_message(message: types.Message):
    # если пользователь просто прислал текст — попробуем считать это кодом
    code_text = message.text.strip()
    if len(code_text) < 3:
        return  # слишком короткий, не код

    # проверим, есть ли у нас такой код
    res, msg = await redeem_code(message.from_user.id, code_text)
    if res is not None:
        await message.answer(f"✅ {msg}")
    else:
        # если это не код — можно игнорировать или ответить «неизвестная команда»
        pass

# --- Игры: пока только «Орёл и решка» с полной логикой ---
@dp.callback_query(lambda cb: cb.data == "game_coin_flip")
async def game_coin_flip_start(cb: types.CallbackQuery):
    await games.coin_flip.play_coin_flip(cb)

# заглушки для остальных игр — чтобы кнопки не ломались
@dp.callback_query(lambda cb: cb.data in [
    "game_tic_tac_toe", "game_roulette", "game_connect_four",
    "game_quick_click", "game_memory"
])
async def game_placeholder(cb: types.CallbackQuery):
    await cb.answer("Эта игра в разработке! Скоро будет доступна.", show_alert=True)

# --- После игры: кнопки «играть снова» / «выйти» ---
@dp.callback_query(lambda cb: cb.data == "game_play_again")
async def game_play_again(cb: types.CallbackQuery):
    # можно вернуть в меню игр или сразу запустить ту же игру
    await cb.message.edit_text("���бери игру снова:", reply_markup=games_menu())
    await cb.answer()

@dp.callback_query(lambda cb: cb.data == "game_exit")
async def game_exit(cb: types.CallbackQuery):
    user = await get_or_create_user(cb.from_user.id, cb.from_user.username or "Аноним")
    text = (
        f"👋 Ты вышел из игры.\n"
        f"Баланс: {user['coins']} монет"
    )
    await cb.message.edit_text(text, reply_markup=main_menu())
    await cb.answer()

# --- Админ: создание кода (упрощённо: через кнопку и ввод в чат) ---
@dp.callback_query(lambda cb: cb.data == "code_create")
async def code_create_start(cb: types.CallbackQuery):
    if cb.from_user.id not in ADMIN_IDS:
        await cb.answer("❌ Доступ запрещён.", show_alert=True)
        return
    await cb.message.edit_text(
        "📝 Введи код (одной строкой):\n"
        "Формат: КОД ТИП НАГРАДА КОЛИЧЕСТВО\n"
        "Пример: MYCODE coins 100 50\n"
        "(тип: coins, case, frame; награда: название или число; кол-во: число активаций)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Отмена", callback_data="menu_codes")]
        ])
    )
    await cb.answer()

@dp.message()
async def handle_admin_code_creation(message: types.Message):
    # очень простая админ-логика: если админ прислал строку с 4 частями — создаём код
    if message.from_user.id not in ADMIN_IDS:
        return

    parts = message.text.strip().split()
    if len(parts) != 4:
        return  # не формат

    code_text, reward_type, reward_name, activations_str = parts
    try:
        activations = int(activations_str)
    except ValueError:
        return

    await create_code(code_text, reward_type, reward_name, activations)
    await message.answer(f"✅ Код {code_text} создан! Тип: {reward_type}, награда: {reward_name}, активаций: {activations}")

# --- Запуск бота (webhook для Railway) ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
