from dataclasses import dataclass

@dataclass
class Room:
    room_id: str
    creator: int
    second_player: int | None = None
    game: str | None = None
    turn: int | None = None
    message_id: int | None = None
    chat_id: int | None = None
    started: bool = False


rooms = {}

players = {}
