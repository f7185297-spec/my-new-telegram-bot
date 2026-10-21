"""E'lon joylash (FSM): rasm -> nom -> tavsif -> narx -> telefon -> chek."""
import logging
import re

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import ADMIN_ID, AD_PRICE, PAYMENT_DETAILS
from database import db
from keyboards.reply import BTN_ADD, cancel_kb, main_menu, phone_kb
from states import AddAd
from utils import send_for_review

router = Router(name="add_ad")
log = logging.getLogger(__name__)

PHONE_RE = re.compile(r"^\+?\d[\d\s\-()]{6,17}$")
MAX_TITLE = 100
MAX_DESC = 600


@router.message(F.text == BTN_ADD)
async def add_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddAd.photo)
    await message.answer(
        "📸 <b>1/5.</b> Mahsulot rasmini yuboring.",
        reply_markup=cancel_kb(),
    )


@router.message(AddAd.photo, F.photo)
async def add_photo(message: Message, state: FSMContext) -> None:
    await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(AddAd.title)
    await message.answer(
        "✏️ <b>2/5.</b> Mahsulot nomi va tavsifini yuboring.\n\n"
        "Birinchi qator — <b>nomi</b>, qolgani — <b>tavsif</b>.\n"
        "Masalan:\n<i>Chevrolet Spark 2018\nHolati a'lo, probeg 60 000 km, bitta egasi.</i>"
    )


@router.message(AddAd.photo)
async def add_photo_invalid(message: Message) -> None:
    await message.answer("Iltimos, mahsulotning <b>rasmini</b> yuboring.")


@router.message(AddAd.title, F.text)
async def add_title(message: Message, state: FSMContext) -> None:
    parts = message.text.strip().split("\n", 1)
    title = parts[0].strip()
    description = parts[1].strip() if len(parts) > 1 else ""

    if not description:
        # Faqat bitta qator yozilgan: nom sifatida ham, tavsif sifatida ham ishlatamiz
        description = title
    if len(title) > MAX_TITLE:
        await message.answer(f"Nom juda uzun (maksimum {MAX_TITLE} belgi). Qisqaroq yozing.")
        return
    if len(description) > MAX_DESC:
        await message.answer(f"Tavsif juda uzun (maksimum {MAX_DESC} belgi). Qisqaroq yozing.")
        return

    await state.update_data(title=title, description=description)
    await state.set_state(AddAd.price)
    await message.answer("💰 <b>3/5.</b> Narxini yozing (masalan: <i>85 000 000 so'm</i> yoki <i>$7500</i>).")


@router.message(AddAd.title)
async def add_title_invalid(message: Message) -> None:
    await message.answer("Iltimos, nom va tavsifni <b>matn</b> ko'rinishida yuboring.")


@router.message(AddAd.price, F.text)
async def add_price(message: Message, state: FSMContext) -> None:
    price = message.text.strip()
    if len(price) > 60:
        await message.answer("Narx juda uzun. Qisqaroq yozing.")
        return
    await state.update_data(price=price)
    await state.set_state(AddAd.phone)
    await message.answer(
        "📞 <b>4/5.</b> Telefon raqamingizni yuboring: pastdagi tugmani bosing yoki "
        "raqamni yozing (masalan: <i>+998901234567</i>).",
        reply_markup=phone_kb(),
    )


@router.message(AddAd.price)
async def add_price_invalid(message: Message) -> None:
    await message.answer("Iltimos, narxni <b>matn</b> ko'rinishida yozing.")


@router.message(AddAd.phone, F.contact | F.text)
async def add_phone(message: Message, state: FSMContext) -> None:
    raw = message.contact.phone_number if message.contact else message.text.strip()
    if not PHONE_RE.match(raw):
        await message.answer("Telefon raqami noto'g'ri. Masalan: <i>+998901234567</i>")
        return

    phone = raw if raw.startswith("+") else f"+{raw}" if message.contact else raw
    await state.update_data(phone=phone)
    await state.set_state(AddAd.receipt)
    await message.answer(
        f"🧾 <b>5/5.</b> E'lon joylash narxi: <b>{AD_PRICE}</b>\n\n"
        f"To'lov rekvizitlari:\n{PAYMENT_DETAILS}\n\n"
        "To'lovni amalga oshirib, <b>chek rasmini</b> (skrinshot) yuboring.",
        reply_markup=cancel_kb(),
    )


@router.message(AddAd.phone)
async def add_phone_invalid(message: Message) -> None:
    await message.answer("Iltimos, tugmani bosing yoki telefon raqamini yozing.")


@router.message(AddAd.receipt, F.photo)
async def add_receipt(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    receipt_id = message.photo[-1].file_id

    ad = await db.create_ad(
        user_id=message.from_user.id,
        username=message.from_user.username,
        photo_id=data["photo_id"],
        title=data["title"],
        description=data["description"],
        price=data["price"],
        phone=data["phone"],
        receipt_id=receipt_id,
    )
    await state.clear()

    await message.answer(
        "✅ E'loningiz qabul qilindi va admin tekshiruviga yuborildi.\n"
        "Natija haqida sizga xabar beramiz.",
        reply_markup=main_menu(message.from_user.id),
    )

    # Adminga: e'lon rasmi + ma'lumot, so'ng chek rasmi va tugmalar
    try:
        await send_for_review(bot, ADMIN_ID, ad)
    except Exception:
        log.exception("Adminga xabar yuborib bo'lmadi (ADMIN_ID to'g'rimi? Admin botni /start qilganmi?)")


@router.message(AddAd.receipt)
async def add_receipt_invalid(message: Message) -> None:
    await message.answer("Iltimos, to'lov <b>chekining rasmini</b> yuboring.")