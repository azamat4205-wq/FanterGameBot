import sqlite3

db = sqlite3.connect("database.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username TEXT,
    coins INTEGER DEFAULT 100,
    wins INTEGER DEFAULT 0,
    loses INTEGER DEFAULT 0,
    cases INTEGER DEFAULT 0,
    frame TEXT DEFAULT 'Нет',
    multiplier INTEGER DEFAULT 1
)
""")

db.commit()


def add_user(user_id, username):
    cursor.execute(
        "INSERT OR IGNORE INTO users(id, username) VALUES(?, ?)",
        (user_id, username)
    )
    db.commit()


def get_user(user_id):
    cursor.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    )
    return cursor.fetchone()


def add_coins(user_id, coins):
    cursor.execute(
        "UPDATE users SET coins = coins + ? WHERE id=?",
        (coins, user_id)
    )
    db.commit()


def remove_coins(user_id, coins):
    cursor.execute(
        "UPDATE users SET coins = coins - ? WHERE id=?",
        (coins, user_id)
    )
    db.commit()


def add_win(user_id):
    cursor.execute(
        "UPDATE users SET wins = wins + 1 WHERE id=?",
        (user_id,)
    )
    db.commit()


def add_lose(user_id):
    cursor.execute(
        "UPDATE users SET loses = loses + 1 WHERE id=?",
        (user_id,)
    )
    db.commit()


def add_case(user_id):
    cursor.execute(
        "UPDATE users SET cases = cases + 1 WHERE id=?",
        (user_id,)
    )
    db.commit()


def set_frame(user_id, frame):
    cursor.execute(
        "UPDATE users SET frame=? WHERE id=?",
        (frame, user_id)
    )
    db.commit()
