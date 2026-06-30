from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import add_user, get_user, get_top
from keyboards import main_menu, play_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await add_user(message.from_user)

    await message.answer(
        f"🎮 <b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
        "Выберите действие ниже 👇",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )


@router.message(F.text == "🎮 Играть")
async def play(message: Message):
    await message.answer(
        "🎲 Выберите режим игры:",
        reply_markup=play_menu()
    )


@router.message(F.text == "👤 Профиль")
async def profile(message: Message):
    user = await get_user(message.from_user.id)

    await message.answer(
        f"👤 <b>{user[2]}</b>\n\n"
        f"🏆 Побед: <b>{user[3]}</b>\n"
        f"💀 Поражений: <b>{user[4]}</b>\n"
        f"🎮 Всего игр: <b>{user[5]}</b>",
        parse_mode="HTML"
    )


@router.message(F.text == "🏆 Рейтинг")
async def rating(message: Message):
    top = await get_top()

    text = "🏆 <b>Топ игроков</b>\n\n"

    for i, player in enumerate(top, start=1):
        text += f"{i}. {player[0]} — {player[1]} побед\n"

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📩 Помощь")
async def help_cmd(message: Message):
    await message.answer(
        "📩 По всем вопросам:\n\n@azamat0158"
    )


@router.message(F.text == "🔙 Назад")
async def back(message: Message):
    await message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )
