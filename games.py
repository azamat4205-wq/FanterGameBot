import random
import string

rooms = {}
players = {}


def generate_room_id():
    while True:
        room_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if room_id not in rooms:
            return room_id


def create_room(user_id: int):
    room_id = generate_room_id()

    rooms[room_id] = {
        "id": room_id,
        "creator": user_id,
        "player2": None,
        "game": None,
        "turn": None,
        "started": False,
        "chat_id": None,
        "message_id": None,
        "play_again": False
    }

    players[user_id] = room_id

    return room_id


def join_room(room_id: str, user_id: int):
    if room_id not in rooms:
        return False

    room = rooms[room_id]

    if room["started"]:
        return False

    if room["creator"] == user_id:
        return False

    room["player2"] = user_id
    room["started"] = True
    room["turn"] = random.choice([room["creator"], room["player2"]])

    players[user_id] = room_id

    return True


def get_room(user_id: int):
    room_id = players.get(user_id)

    if not room_id:
        return None

    return rooms.get(room_id)


def remove_room(room_id: str):
    room = rooms.get(room_id)

    if not room:
        return

    if room["creator"] in players:
        del players[room["creator"]]

    if room["player2"] in players:
        del players[room["player2"]]

    del rooms[room_id]


def leave_game(user_id: int):
    room = get_room(user_id)

    if not room:
        return

    remove_room(room["id"])
