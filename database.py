import sqlite3
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_file="game.db"):
        """Инициализация подключения к БД"""
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
        logger.info("База данных успешно подключена и проверена.")

    def _create_tables(self):
        """Создание таблиц, если их нет"""
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            coins INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        );
        """
        self.cursor.execute(create_users_table)
        self.conn.commit()

    async def create_user(self, user_id: int, first_name: str):
        """Создает нового пользователя, если его нет"""
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, first_name, coins, level) VALUES (?, ?, 0, 1)",
                (user_id, first_name)
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            return False

    async def get_user(self, user_id: int):
        """Получает данные пользователя по ID"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = self.cursor.fetchone()
            if row:
                return {
                    "user_id": row,
                    "first_name": row,
                    "coins": row,
                    "level": row
                }
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя: {e}")
            return None

    async def get_top(self, limit: int = 10):
        """Получает топ игроков по количеству монет"""
        try:
            self.cursor.execute(
                "SELECT first_name, coins FROM users ORDER BY coins DESC LIMIT ?",
                (limit,)
            )
            rows = self.cursor.fetchall()
            return [
                {"first_name": row, "coins": row}
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Ошибка при получении топа: {e}")
            return []

    def close(self):
        """Закрывает соединение с БД"""
        if self.conn:
            self.conn.close()
            
