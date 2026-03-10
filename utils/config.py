import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

    CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
    CHAT_ID = int(os.getenv("CHAT_ID"))

    ADMIN_ID = int(os.getenv("ADMIN_ID"))


class Tariffs:
    MONTH = {
        "name": "1 месяц",
        "price": 1499,  # цена в центах ($14,99)
        "duration_days": 30
    }

    THREE_MONTHS = {
        "name": "3 месяца",
        "price": 3999,  # $39,99
        "duration_days": 90
    }