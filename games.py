import random
import string

rooms = {}
players = {}


def create_room(user_id: int):
    while True:
        room_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if room_id not in rooms:
            break

    rooms[room_id] = {
        "creator": user_id,
        "player2": None,
        "game": None,
        "turn": None,
        "started": False,
        "message_id": None,
        "chat_id": None
    }

    players[user_id] = room_id
    return room_id


def join_room(room_id: str, user_id: int):
    if room_id not in rooms:
        return False

    room = rooms[room_id]

    if room["player2"] is not None:
        return False

    room["player2"] = user_id
    room["started"] = True

    room["turn"] = random.choice([room["creator"], room["player2"]])

    players[user_id] = room_id

    return True


def get_room(user_id: int):
    room_id = players.get(user_id)

    if room_id:
        return rooms.get(room_id)

    return None


def leave_room(user_id: int):
    room_id = players.get(user_id)

    if not room_id:
        return

    room = rooms.get(room_id)

    if room:
        if room["creator"] in players:
            del players[room["creator"]]

        if room["player2"] and room["player2"] in players:
            del players[room["player2"]]

        del rooms[room_id]
