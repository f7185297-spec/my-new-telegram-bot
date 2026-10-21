"""Yordamchi funksiyalar: e'lonni matn ko'rinishiga keltirish."""
from html import escape

from aiogram import Bot

from database.models import Ad, AdStatus
from keyboards.inline import admin_review_kb

STATUS_LABELS = {
    AdStatus.PENDING: "⏳ Tekshiruvda",
    AdStatus.ACTIVE: "🟢 Faol",
    AdStatus.REJECTED: "🔴 Rad etilgan",
}


def format_ad(ad: Ad, *, show_status: bool = False) -> str:
    """Foydalanuvchiga ko'rsatiladigan e'lon matni (HTML)."""
    lines = [
        f"<b>{escape(ad.title)}</b>",
        f"💰 Narxi: {escape(ad.price)}",
        "",
        escape(ad.description),
        "",
        f"📞 Tel: {escape(ad.phone)}",
    ]
    if show_status:
        lines += ["", STATUS_LABELS.get(ad.status, ad.status)]
    return "\n".join(lines)


def format_ad_for_admin(ad: Ad) -> str:
    """Admin uchun e'lon matni (egasi haqida ma'lumot bilan)."""
    owner = f'<a href="tg://user?id={ad.user_id}">Foydalanuvchi</a>'
    if ad.username:
        owner += f" (@{escape(ad.username)})"
    return (
        f"🆕 <b>Yangi e'lon #{ad.id}</b>\n\n"
        f"{format_ad(ad)}\n\n"
        f"👤 {owner}\n"
        f"🆔 <code>{ad.user_id}</code>"
    )


async def send_for_review(bot: Bot, chat_id: int, ad: Ad) -> None:
    """Adminga e'lon rasmi + ma'lumot, so'ng chek rasmi va Tasdiqlash/Rad etish tugmalarini yuboradi."""
    await bot.send_photo(chat_id, ad.photo_id, caption=format_ad_for_admin(ad))
    await bot.send_photo(
        chat_id,
        ad.receipt_id,
        caption=f"🧾 <b>To'lov cheki</b> — e'lon #{ad.id}",
        reply_markup=admin_review_kb(ad.id),
    )