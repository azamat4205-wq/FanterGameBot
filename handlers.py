from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import add_user, get_user, get_top
from keyboards import main_menu, play_menu
from games import create_room

router = Router()


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
        "🎲 Выберите режим игры:",
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

    await message.answer(
        f"🎮 Комната создана!\n\n"
        f"Код комнаты:\n"
        f"`{code}`\n\n"
        "Скоро появится приглашение по ссылке.",
        parse_mode="Markdown"
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
