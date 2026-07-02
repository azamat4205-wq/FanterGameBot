import random


def create_coin_game(room):
    room["game"] = "coin"
    room["coin"] = {
        "creator_choice": None,
        "player2_choice": None,
        "winner": None
    }


def choose_side(room, user_id, side):
    if user_id == room["creator"]:
        room["coin"]["creator_choice"] = side
    elif user_id == room["player2"]:
        room["coin"]["player2_choice"] = side

    if (
        room["coin"]["creator_choice"] is None
        or room["coin"]["player2_choice"] is None
    ):
        return None

    result = random.choice(["Орёл", "Решка"])

    creator = room["coin"]["creator_choice"]
    player2 = room["coin"]["player2_choice"]

    if creator == result:
        winner = room["creator"]
    elif player2 == result:
        winner = room["player2"]
    else:
        winner = None

    room["coin"]["winner"] = winner

    return result, winner
