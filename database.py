import sqlite3

db = sqlite3.connect("players.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    coins INTEGER DEFAULT 100,
    wins INTEGER DEFAULT 0,
    loses INTEGER DEFAULT 0
)
""")

db.commit()


def register(user):
    cursor.execute(
        "SELECT user_id FROM players WHERE user_id=?",
        (user.id,)
    )

    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO players(user_id, username) VALUES(?,?)",
            (
                user.id,
                user.first_name
            )
        )
        db.commit()
