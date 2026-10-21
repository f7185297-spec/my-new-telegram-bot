# Yaypan bozori — Telegram bot

`aiogram 3.x` + `SQLAlchemy (async)` + `SQLite` asosidagi e'lonlar boti.

## Ishga tushirish

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # BOT_TOKEN va ADMIN_ID ni to'ldiring
python bot.py
```

> Admin botga kamida bir marta `/start` yozgan bo'lishi kerak, aks holda bot unga xabar yubora olmaydi.

## Tuzilma

```
bot.py              — kirish nuqtasi
config.py           — .env sozlamalari
states.py           — FSM holatlari
utils.py            — e'lonni matnga aylantirish
database/           — modellar va CRUD (async SQLAlchemy + aiosqlite)
keyboards/          — reply va inline klaviaturalar
handlers/
  user.py           — /start, qidiruv, mening e'lonlarim
  add_ad.py         — e'lon joylash (FSM)
  admin.py          — tasdiqlash / sabab bilan rad etish
```

## Ishlash tartibi

1. Foydalanuvchi «➕ E'lon joylash» orqali rasm, nom/tavsif, narx, telefon va to'lov chekini yuboradi.
2. Admin e'lon va chekni oladi → «✅ Tasdiqlash» yoki «❌ Rad etish» (sabab yoziladi).
3. Tasdiqlangan e'lonlar «🔍 E'lon qidirish» da ko'rinadi.
4. «📂 Mening e'lonlarim» da «✅ Sotildi» / «❌ O'chirish» e'lonni bazadan o'chiradi.