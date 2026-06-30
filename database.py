import aiosqlite

DB_NAME = "bot.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            games INTEGER DEFAULT 0
        )
        """)
        await db.commit()


async def add_user(user):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT user_id FROM users WHERE user_id=?",
            (user.id,)
        )

        if await cursor.fetchone() is None:
            await db.execute(
                """
                INSERT INTO users(user_id, username, first_name)
                VALUES(?, ?, ?)
                """,
                (
                    user.id,
                    user.username,
                    user.first_name
                )
            )
            await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id=?",
            (user_id,)
        )
        return await cursor.fetchone()


async def update_stats(user_id, win: bool):
    async with aiosqlite.connect(DB_NAME) as db:
        if win:
            await db.execute("""
                UPDATE users
                SET wins = wins + 1,
                    games = games + 1
                WHERE user_id = ?
            """, (user_id,))
        else:
            await db.execute("""
                UPDATE users
                SET losses = losses + 1,
                    games = games + 1
                WHERE user_id = ?
            """, (user_id,))

        await db.commit()


async def get_top(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT first_name, wins
            FROM users
            ORDER BY wins DESC
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()
