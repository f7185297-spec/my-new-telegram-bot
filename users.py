"""Foydalanuvchi: /start, e'lon qidirish, mening e'lonlarim, bekor qilish."""
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from keyboards.inline import MyAdAction, my_ad_kb
from keyboards.reply import BTN_CANCEL, BTN_MY_ADS, BTN_SEARCH, cancel_kb, main_menu
from states import SearchState
from utils import format_ad

router = Router(name="user")


# ---------- Start va bekor qilish ----------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "👋 <b>Yaypan bozori</b>ga xush kelibsiz!\n\n"
        "Bu yerda mahsulot qidirishingiz yoki o'z e'loningizni joylashingiz mumkin.",
        reply_markup=main_menu(message.from_user.id),
    )


@router.message(Command("cancel"))
@router.message(F.text == BTN_CANCEL)
async def cancel_any(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=main_menu(message.from_user.id))


# ---------- Qidiruv ----------

@router.message(F.text == BTN_SEARCH)
async def search_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchState.query)
    await message.answer(
        "🔍 Nima qidiryapsiz? Mahsulot nomini yozing (masalan: <i>Spark</i> yoki <i>Telefon</i>).",
        reply_markup=main_menu(message.from_user.id),
    )


async def _do_search(message: Message) -> None:
    query = (message.text or "").strip()
    if len(query) < 2:
        await message.answer("Iltimos, kamida 2 ta belgidan iborat so'z yozing.")
        return

    ads = await db.search_ads(query)
    if not ads:
        await message.answer(f"😔 «{query}» bo'yicha e'lon topilmadi. Boshqa so'z bilan urinib ko'ring.")
        return

    await message.answer(f"✅ Topilgan e'lonlar: {len(ads)} ta")
    for ad in ads:
        await message.answer_photo(ad.photo_id, caption=format_ad(ad))


@router.message(StateFilter(SearchState.query, None), F.text, ~F.text.startswith("/"))
async def search_by_text(message: Message) -> None:
    """Qidiruv holatida yoki oddiy matn yozilganda qidiradi."""
    await _do_search(message)


# ---------- Mening e'lonlarim ----------

@router.message(F.text == BTN_MY_ADS)
async def my_ads(message: Message, state: FSMContext) -> None:
    await state.clear()
    ads = await db.get_user_ads(message.from_user.id)
    if not ads:
        await message.answer(
            "Sizda hali e'lonlar yo'q. «➕ E'lon joylash» tugmasini bosing.",
            reply_markup=main_menu(message.from_user.id),
        )
        return

    await message.answer(
        f"📂 Sizning e'lonlaringiz: {len(ads)} ta",
        reply_markup=main_menu(message.from_user.id),
    )
    for ad in ads:
        await message.answer_photo(
            ad.photo_id,
            caption=format_ad(ad, show_status=True),
            reply_markup=my_ad_kb(ad.id),
        )


@router.callback_query(MyAdAction.filter())
async def my_ad_action(callback: CallbackQuery, callback_data: MyAdAction) -> None:
    deleted = await db.delete_ad(callback_data.ad_id, callback.from_user.id)
    if not deleted:
        await callback.answer("E'lon topilmadi yoki allaqachon o'chirilgan.", show_alert=True)
        try:
            await callback.message.delete()
        except Exception:
            pass
        return

    if callback_data.action == "sold":
        note = "✅ Tabriklaymiz! E'lon sotildi deb belgilandi va bazadan o'chirildi."
    else:
        note = "🗑 E'lon o'chirildi."

    await callback.answer(note, show_alert=True)
    try:
        await callback.message.delete()
    except Exception:
        await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(note)