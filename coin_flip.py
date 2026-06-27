import random
from aiogram import types
from keyboards import after_game
from database import update_coins, add_win, add_loss, get_or_create_user

async def play_coin_flip(cb: types.CallbackQuery):
    user = await get_or_create_user(cb.from_user.id, cb.from_user.username or "Аноним")
    result = random.choice(["Орёл", "Решка"])
    win = random.random() < 0.5  # 50/50
    reward = 10 if win else 5

    await update_coins(cb.from_user.id, reward)
    if win:
        await add_win(cb.from_user.id)
        text = f"���ёл и решка: выпало **«{result}»**! Ты победил! +{reward} монет."
    else:
        await add_loss(cb.from_user.id)
        text =
