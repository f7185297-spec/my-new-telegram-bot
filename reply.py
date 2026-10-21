"""Oddiy (Reply) klaviaturalar."""
from typing import Optional

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from config import ADMIN_ID

BTN_SEARCH = "🔍 E'lon qidirish"
BTN_ADD = "➕ E'lon joylash"
BTN_MY_ADS = "📂 Mening e'lonlarim"
BTN_ADMIN = "👑 Admin panel"
BTN_CANCEL = "❌ Bekor qilish"
BTN_SEND_PHONE = "📱 Raqamimni yuborish"


def main_menu(user_id: Optional[int] = None) -> ReplyKeyboardMarkup:
    """Asosiy menyu. «Admin panel» tugmasi faqat ADMIN_ID egasiga ko'rinadi."""
    rows = [
        [KeyboardButton(text=BTN_SEARCH)],
        [KeyboardButton(text=BTN_ADD), KeyboardButton(text=BTN_MY_ADS)],
    ]
    if user_id is not None and user_id == ADMIN_ID:
        rows.append([KeyboardButton(text=BTN_ADMIN)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True,
    )


def phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_SEND_PHONE, request_contact=True)],
            [KeyboardButton(text=BTN_CANCEL)],
        ],
        resize_keyboard=True,
    )
