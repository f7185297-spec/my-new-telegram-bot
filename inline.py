"""Inline klaviaturalar va callback ma'lumotlari."""
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class AdminAction(CallbackData, prefix="adm"):
    action: str  # "approve" | "reject"
    ad_id: int


class MyAdAction(CallbackData, prefix="my"):
    action: str  # "sold" | "delete"
    ad_id: int


class AdminMenu(CallbackData, prefix="amenu"):
    action: str  # "pending" | "stats"


def admin_menu_kb(pending_count: int = 0) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⏳ Kutilayotgan e'lonlar ({pending_count})",
                    callback_data=AdminMenu(action="pending").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data=AdminMenu(action="stats").pack(),
                )
            ],
        ]
    )


def admin_review_kb(ad_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=AdminAction(action="approve", ad_id=ad_id).pack(),
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish (Sabab belgilash)",
                    callback_data=AdminAction(action="reject", ad_id=ad_id).pack(),
                ),
            ]
        ]
    )


def my_ad_kb(ad_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Sotildi",
                    callback_data=MyAdAction(action="sold", ad_id=ad_id).pack(),
                ),
                InlineKeyboardButton(
                    text="❌ O'chirish",
                    callback_data=MyAdAction(action="delete", ad_id=ad_id).pack(),
                ),
            ]
        ]
    )