"""Admin paneli: e'lonni tasdiqlash yoki sabab bilan rad etish."""
import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from database import db
from database.models import AdStatus
from keyboards.inline import AdminAction, AdminMenu, admin_menu_kb
from keyboards.reply import BTN_ADMIN
from states import AdminReject
from utils import send_for_review

router = Router(name="admin")
# Bu router'dagi barcha handlerlar faqat admin uchun
router.message.filter(F.from_user.id == ADMIN_ID)
router.callback_query.filter(F.from_user.id == ADMIN_ID)

log = logging.getLogger(__name__)


async def _notify(bot: Bot, user_id: int, text: str) -> None:
    try:
        await bot.send_message(user_id, text)
    except Exception:
        log.warning("Foydalanuvchi %s ga xabar yuborib bo'lmadi (botni bloklagan bo'lishi mumkin)", user_id)


async def _finish_review(callback: CallbackQuery, status_line: str) -> None:
    """Admin xabaridagi tugmalarni olib tashlab, natijani yozib qo'yadi."""
    msg = callback.message
    try:
        await msg.edit_caption(caption=f"{msg.html_text}\n\n{status_line}", reply_markup=None)
    except Exception:
        await msg.edit_reply_markup(reply_markup=None)


# ---------- Admin panel menyusi ----------
# Bu handler FSM handlerlaridan oldin turishi kerak, shunda tugma har doim ishlaydi.

@router.message(Command("admin"))
@router.message(F.text == BTN_ADMIN)
async def admin_panel(message: Message, state: FSMContext) -> None:
    await state.clear()
    stats = await db.get_stats()
    await message.answer(
        "👑 <b>Admin panel</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=admin_menu_kb(stats["pending"]),
    )


@router.callback_query(AdminMenu.filter(F.action == "pending"))
async def show_pending(callback: CallbackQuery, bot: Bot) -> None:
    ads = await db.get_pending_ads()
    await callback.answer()
    if not ads:
        await callback.message.answer("✅ Kutilayotgan e'lonlar yo'q.")
        return

    await callback.message.answer(f"⏳ Kutilayotgan e'lonlar: {len(ads)} ta")
    for ad in ads:
        await send_for_review(bot, callback.message.chat.id, ad)


@router.callback_query(AdminMenu.filter(F.action == "stats"))
async def show_stats(callback: CallbackQuery) -> None:
    s = await db.get_stats()
    total = s["pending"] + s["active"] + s["rejected"]
    await callback.answer()
    await callback.message.answer(
        "📊 <b>Statistika</b>\n\n"
        f"📦 Jami e'lonlar: <b>{total}</b>\n"
        f"⏳ Kutilmoqda: <b>{s['pending']}</b>\n"
        f"🟢 Faol: <b>{s['active']}</b>\n"
        f"🔴 Rad etilgan: <b>{s['rejected']}</b>\n"
        f"👥 E'lon bergan foydalanuvchilar: <b>{s['users']}</b>"
    )


# ---------- Tasdiqlash / Rad etish ----------

@router.callback_query(AdminAction.filter(F.action == "approve"))
async def approve(callback: CallbackQuery, callback_data: AdminAction, bot: Bot) -> None:
    ad = await db.set_status(callback_data.ad_id, AdStatus.ACTIVE)
    if ad is None:
        await callback.answer("Bu e'lon topilmadi yoki allaqachon ko'rib chiqilgan.", show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    await callback.answer("Tasdiqlandi ✅")
    await _finish_review(callback, "✅ <b>Tasdiqlandi</b>")
    await _notify(bot, ad.user_id, f"✅ E'loningiz tasdiqlandi!\n«{escape(ad.title)}» endi qidiruvda ko'rinadi.")


@router.callback_query(AdminAction.filter(F.action == "reject"))
async def reject_start(callback: CallbackQuery, callback_data: AdminAction, state: FSMContext) -> None:
    ad = await db.get_ad(callback_data.ad_id)
    if ad is None or ad.status != AdStatus.PENDING:
        await callback.answer("Bu e'lon topilmadi yoki allaqachon ko'rib chiqilgan.", show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    await state.set_state(AdminReject.reason)
    await state.update_data(
        ad_id=ad.id,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
    )
    await callback.answer()
    await callback.message.answer(
        f"✍️ E'lon #{ad.id} ni rad etish sababini yozing.\nBekor qilish: /cancel"
    )


@router.message(Command("cancel"), AdminReject.reason)
async def reject_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Rad etish bekor qilindi. Tugmalar o'z joyida turibdi.")


@router.message(AdminReject.reason, F.text)
async def reject_finish(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    reason = message.text.strip()
    ad = await db.set_status(data["ad_id"], AdStatus.REJECTED, reason)
    await state.clear()

    if ad is None:
        await message.answer("Bu e'lon topilmadi yoki allaqachon ko'rib chiqilgan.")
        return

    # Chek xabaridagi tugmalarni yangilaymiz
    try:
        await bot.edit_message_caption(
            chat_id=data["chat_id"],
            message_id=data["message_id"],
            caption=f"🧾 <b>To'lov cheki</b> — e'lon #{ad.id}\n\n❌ <b>Rad etildi</b>\nSabab: {escape(reason)}",
            reply_markup=None,
        )
    except Exception:
        pass

    await message.answer(f"❌ E'lon #{ad.id} rad etildi, foydalanuvchiga xabar yuborildi.")
    await _notify(
        bot,
        ad.user_id,
        f"❌ Afsuski, «{escape(ad.title)}» e'loningiz rad etildi.\n\n<b>Sabab:</b> {escape(reason)}",
    )


@router.message(AdminReject.reason)
async def reject_invalid(message: Message) -> None:
    await message.answer("Iltimos, sababni matn ko'rinishida yozing (yoki /cancel).")