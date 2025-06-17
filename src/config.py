import os
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# Получаем токен
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Не указан TELEGRAM_BOT_TOKEN в .env")