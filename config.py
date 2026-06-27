import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬ_СЮДА_ТОКЕН_ОТ_BOTFATHER")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://ТВОЙ_PROJECT.railway.app")
PORT = int(os.getenv("PORT", 8000))
ADMIN_IDS = [7795629827]  # Твой ID для админ-функций
DB_PATH = "bot.db"
