"""Sozlamalar: .env faylidan o'qiladi."""
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        sys.exit(f"❌ .env faylida {name} ko'rsatilmagan. .env.example ni nusxalab to'ldiring.")
    return value


BOT_TOKEN: str = _require("BOT_TOKEN")

try:
    ADMIN_ID: int = int(_require("ADMIN_ID"))
except ValueError:
    sys.exit("❌ ADMIN_ID raqam bo'lishi kerak (masalan: 123456789).")

# E'lon joylash uchun to'lov rekvizitlari va narxi (.env orqali o'zgartiriladi)
PAYMENT_DETAILS: str = os.getenv("PAYMENT_DETAILS", "💳 Karta: 8600 0000 0000 0000\n👤 Ega: Falonchi P.")
AD_PRICE: str = os.getenv("AD_PRICE", "10 000 so'm")

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///yaypan.db")