import random
import string

rooms = {}
players = {}


def generate_room_code():
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in rooms:
            return code


def create_room(user_id: int):
    if user_id in players:
        return players[user_id]

    code = generate_room_code()

    rooms[code] = {
        "code": code,
        "creator": user_id,
        "player2": None,
        "game": None,
        "turn": None,
        "started": False,
        "chat_id": None,
        "message_id": None,
        "data": {}
    }

    players[user_id] = code

    return code


def join_room(code: str, user_id: int):
    if code not in rooms:
        return False

    room = rooms[code]

    if room["started"]:
        return False

    if room["creator"] == user_id:
        return False

    room["player2"] = user_id
    room["started"] = True
    room["turn"] = random.choice([room["creator"], room["player2"]])

    players[user_id] = code

    return True


def get_room(user_id: int):
    code = players.get(user_id)

    if not code:
        return None

    return rooms.get(code)


def remove_room(code: str):
    room = rooms.get(code)

    if not room:
        return

    players.pop(room["creator"], None)

    if room["player2"]:
        players.pop(room["player2"], None)

    rooms.pop(code, None)
