import os
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не найден BOT_TOKEN в .env!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище комнат
rooms = {}
scores = {}

def get_rps_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✊ Камень", callback_data="rps_rock"),
        InlineKeyboardButton(text="✂️ Ножницы", callback_data="rps_scissors"),
        InlineKeyboardButton(text="📄 Бумага", callback_data="rps_paper"),
    )
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message):
    await message.answer(
        "👋 Привет! Это игровой бот.\n\n"
        "Напиши /startgame, чтобы создать комнату и получить ссылку для друга.",
        reply_markup=get_rps_keyboard(),
    )

@dp.message(Command("startgame"))
async def start_game(message):
    user_id = message.from_user.id
    # Если уже есть комната — не создаём новую
    for data in rooms.values():
        if data["player1"] == user_id or data["player2"] == user_id:
            await message.answer("У тебя уже есть активная комната!")
            return

    room_code = str(random.randint(100000, 999999))
    rooms[room_code] = {
        "player1": user_id,
        "player2": None,
        "p1_name": message.from_user.first_name,
        "p2_name": "",
        "p1_move": None,
        "p2_move": None,
    }

    # Генерируем ссылку: t.me/bot_username?start=join_КОД
    # Чтобы ссылка работала, у бота должен быть username (например, @my_super_game_bot)
    bot_info = await bot.get_me()
    invite_link = f"t.me/{bot_info.username}?start=join_{room_code}"

    await message.answer(
        f"✅ Комната создана! Код: `{room_code}`\n\n"
        f"Отправь другу эту ссылку:\n{invite_link}",
        parse_mode="Markdown",
    )

# Обработка ссылки (когда друг нажимает на неё)
@dp.message(F.command == "start")
async def handle_start_with_arg(message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("join_"):
        room_code = args[1][5:]  # убираем "join_"
        # Дальше логика присоединения — как в /joingame
        await join_game_logic(message, room_code)
        return
    # Если просто /start без аргументов — обычный привет
    await cmd_start(message)

async def join_game_logic(message, room_code):
    if room_code not in rooms:
        await message.answer("❌ Такой комнаты не существует. Попроси друга создать новую.")
        return

    data = rooms[room_code]
    if data["player2"] is not None:
        await message.answer("❌ В этой комнате уже есть два игрока.")
        return

    user = message.from_user
    if data["player1"] == user.id:
        await message.answer("Ты уже создатель этой комнаты.")
        return

    # Присоединяем второго игрока
    data["player2"] = user.id
    data["p2_name"] = user.first_name

    await message.answer(
        f"✅ Ты присоединился к комнате!\nНажимай кнопки по очереди, чтобы сыграть.",
        reply_markup=get_rps_keyboard(),
    )

    try:
        await bot.send_message(
            data["player1"],
            f"🎉 Твой друг {data['p2_name']} присоединился! Нажимайте кнопки по очереди.",
        )
    except:
        pass

@dp.callback_query(F.data.startswith("rps_"))
async def handle_rps(callback):
    user = callback.from_user
    user_id = user.id

    target_room = None
    for data in rooms.values():
        if data["player1"] == user_id or data["player2"] == user_id:
            target_room = data
            break

    if not target_room:
        await callback.answer("❌ Ты не в комнате. Напиши /startgame, чтобы создать новую.")
        return

    choice_map = {
        "rps_rock": "камень",
        "rps_scissors": "ножницы",
        "rps_paper": "бумага",
    }
    user_choice = choice_map[callback.data]

    if target_room["player1"] == user_id:
        target_room["p1_move"] = user_choice
    else:
        target_room["p2_move"] = user_choice

    p1_move = target_room["p1_move"]
    p2_move = target_room["p2_move"]

    if p1_move is None or p2_move is None:
        await callback.answer("��дём, пока соперник сделает ход...")
        return

    defeats = {"камень": "ножницы", "ножницы": "бумага", "бумага": "камень"}
    result_text = ""
    winner_id = None

    if p1_move == p2_move:
        result_text = f"🤝 Ничья! Оба выбрали {p1_move}."
    elif defeats[p1_move] == p2_move:
        result_text = f"🎉 {target_room['p1_name']} победил! ({p1_move} против {p2_move})"
        winner_id = target_room["player1"]
    else:
        result_text = f"🎉 {target_room['p2_name']} победил! ({p2_move} против {p1_move})"
        winner_id = target_room["player2"]

    if winner_id:
        scores[winner_id] = scores.get(winner_id, 0) + 1

    target_room["p1_move"] = None
    target_room["p2_move"] = None

    try:
        await bot.send_message(target_room["player1"], result_text, reply_markup=get_rps_keyboard())
        await bot.send_message(target_room["player2"], result_text, reply_markup=get_rps_keyboard())
    except:
        pass

    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
          
