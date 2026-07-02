from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

from database import add_user, get_user, get_top
from keyboards import main_menu, play_menu, room_keyboard
from games import create_room, join_room
from config import BOT_LINK

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_with_link(message: Message, command: CommandObject):
    await add_user(message.from_user)

    if command.args and command.args.startswith("room_"):
        code = command.args.replace("room_", "")

        if join_room(code, message.from_user.id):
            await message.answer(
                "🎉 Ты успешно подключился к комнате!\n\n"
                "⌛ Ожидайте, сейчас появится выбор игры."
            )
        else:
            await message.answer(
                "❌ Не удалось подключиться к комнате.\n"
                "Возможно, игра уже началась или комната не существует."
            )
        return


@router.message(CommandStart())
async def start(message: Message):
    await add_user(message.from_user)

    text = (
        f"🎮 Добро пожаловать, {message.from_user.first_name}!\n\n"
        "Выбери действие ниже 👇"
    )

    await message.answer(
        text,
        reply_markup=main_menu()
    )


@router.message(F.text == "🎮 Играть")
async def play(message: Message):
    await message.answer(
        "🎲 Выберите игру:",
        reply_markup=play_menu()
    )


@router.message(F.text == "🤖 Играть с ботом")
async def bot_game(message: Message):
    await message.answer(
        "🤖 Скоро здесь появятся игры с ботом!"
    )


@router.message(F.text == "👥 Играть с другом")
async def friend_game(message: Message):
    code = create_room(message.from_user.id)

    link = f"{BOT_LINK}?start=room_{code}"

    await message.answer(
        "🎮 Комната создана!\n\n"
        f"🆔 Код: {code}\n\n"
        "Нажми кнопку ниже и отправь ссылку другу 👇",
        reply_markup=room_keyboard(link)
    )


@router.message(F.text == "👤 Профиль")
async def profile(message: Message):
    user = await get_user(message.from_user.id)

    await message.answer(
        f"👤 {user[2]}\n\n"
        f"🏆 Побед: {user[3]}\n"
        f"💀 Поражений: {user[4]}\n"
        f"🎮 Всего игр: {user[5]}"
    )


@router.message(F.text == "🏆 Рейтинг")
async def rating(message: Message):
    top = await get_top()

    text = "🏆 Топ игроков\n\n"

    for i, player in enumerate(top, 1):
        text += f"{i}. {player[0]} — {player[1]} побед\n"

    await message.answer(text)


@router.message(F.text == "📩 Помощь")
async def help_cmd(message: Message):
    await message.answer(
        "📩 Помощь\n\n"
        "Связь: @azamat0158"
    )


@router.message(F.text == "🔙 Назад")
async def back(message: Message):
    await message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )
