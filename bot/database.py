import aiosqlite
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                coins INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                last_bonus DATE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id INTEGER,
                item_type TEXT,      -- 'case', 'frame', 'multiplier'
                item_name TEXT,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS case_items (
                case_id INTEGER,
                item_type TEXT,
                item_name TEXT,
                chance REAL,
                FOREIGN KEY(case_id) REFERENCES cases(case_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS codes (
                code_text TEXT PRIMARY KEY,
                reward_type TEXT,    -- 'coins', 'case', 'frame'
                reward_name TEXT,
                activations_total INTEGER,
                activations_used INTEGER DEFAULT 0
            )
        """)
        await db.commit()

# --- Users ---
async def get_or_create_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = await cur.fetchone()
        if not user:
            await db.execute(
                "INSERT INTO users (user_id, username, coins, wins, losses) VALUES (?, ?, 0, 0, 0)",
                (user_id, username)
            )
            await db.commit()
            cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = await cur.fetchone()
        return dict(user)

async def update_coins(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

async def add_win(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET wins = wins + 1 WHERE user_id = ?", (user_id,))
        await db.commit()

async def add_loss(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET losses = losses + 1 WHERE user_id = ?", (user_id,))
        await db.commit()

# --- Inventory ---
async def add_inventory_item(user_id: int, item_type: str, item_name: str, qty: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO inventory (user_id, item_type, item_name, quantity)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, item_type, item_name) DO UPDATE SET quantity = quantity + ?
        """, (user_id, item_type, item_name, qty, qty))
        await db.commit()

async def get_inventory(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM inventory WHERE user_id = ?", (user_id,))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

# --- Cases ---
async def create_case(name: str, description: str, items: list):
    # items: [{type, name, chance}, ...]
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("INSERT INTO cases (name, description) VALUES (?, ?)", (name, description))
        case_id = cur.lastrowid
        for i in items:
            await db.execute(
                "INSERT INTO case_items (case_id, item_type, item_name, chance) VALUES (?, ?, ?, ?)",
                (case_id, i["type"], i["name"], i["chance"])
            )
        await db.commit()
        return case_id

async def open_case(user_id: int, case_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Получаем предметы кейса
        cur = await db.execute("SELECT * FROM case_items WHERE case_id = ?", (case_id,))
        items = await cur.fetchall()
        import random
        r = random.random()
        acc = 0.0
        won_item = None
        for row in items:
            acc += row["chance"]
            if r <= acc:
                won_item = dict(row)
                break
        if won_item:
            await add_inventory_item(user_id, won_item["item_type"], won_item["item_name"])
        return won_item

# --- Codes ---
async def create_code(code_text: str, reward_type: str, reward_name: str, activations: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO codes (code_text, reward_type, reward_name, activations_total)
            VALUES (?, ?, ?, ?)
        """, (code_text, reward_type, reward_name, activations))
        await db.commit()

async def redeem_code(user_id: int, code_text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM codes WHERE code_text = ?", (code_text,))
        code = await cur.fetchone()
        if not code:
            return None, "Код не найден."
        if code["activations_used"] >= code["activations_total"]:
            # Удаляем код, если лимит исчерпан
            await db.execute("DELETE FROM codes WHERE code_text = ?", (code_text,))
            await db.commit()
            return None, "Этот код больше не действует."
        # Выдаем награду
        reward_type = code["reward_type"]
        reward_name = code["reward_name"]
        if reward_type == "coins":
            await update_coins(user_id, int(reward_name))
        elif reward_type == "case":
            # Тут можно сделать выдачу конкретного кейса по ID, пока просто добавим кейс
            await add_inventory_item(user_id, "case", reward_name)
        elif reward_type == "frame":
            await add_inventory_item(user_id, "frame", reward_name)

        await db.execute("UPDATE codes SET activations_used = activations_used + 1 WHERE code_text = ?", (code_text,))
        await db.commit()
        return code, "Награда получена!"

# --- Daily Bonus ---
async def check_daily_bonus(user_id: int):
    from datetime import date
    today = str(date.today())
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT last_bonus FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        last = row["last_bonus"] if row else None
        if last == today:
            return False, 0
        # Даем бонус
        bonus = 20
        if random.random() < 0.3: bonus = 50
        if random.random() < 0.1: bonus = 100
        await update_coins(user_id, bonus)
        await db.execute("UPDATE users SET last_bonus = ? WHERE user_id = ?", (today, user_id))
        await db.commit()
        return True, bonus

# --- Leaderboard ---
async def get_top_users(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT user_id, username, coins, wins FROM users
            ORDER BY coins DESC, wins DESC
            LIMIT ?
        """, (limit,))
        return [dict(r) for r in await cur.fetchall()]
