"""Ma'lumotlar bazasi: engine, sessiya va CRUD funksiyalari."""
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import DATABASE_URL
from database.models import Ad, AdStatus, Base

engine = create_async_engine(DATABASE_URL, echo=False)
session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    """Jadvallarni yaratadi (mavjud bo'lsa tegmaydi)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_ad(
    *,
    user_id: int,
    username: Optional[str],
    photo_id: str,
    title: str,
    description: str,
    price: str,
    phone: str,
    receipt_id: str,
) -> Ad:
    ad = Ad(
        user_id=user_id,
        username=username,
        photo_id=photo_id,
        title=title,
        description=description,
        price=price,
        phone=phone,
        receipt_id=receipt_id,
        search_text=f"{title} {description}".lower(),
        status=AdStatus.PENDING,
    )
    async with session_maker() as session:
        session.add(ad)
        await session.commit()
        await session.refresh(ad)
    return ad


async def get_ad(ad_id: int) -> Optional[Ad]:
    async with session_maker() as session:
        return await session.get(Ad, ad_id)


async def search_ads(query: str, limit: int = 10) -> Sequence[Ad]:
    """Faol e'lonlardan qidiradi. So'rovdagi barcha so'zlar nom/tavsifda bo'lishi kerak."""
    words = [w for w in query.lower().split() if w]
    if not words:
        return []
    stmt = select(Ad).where(Ad.status == AdStatus.ACTIVE)
    for word in words:
        stmt = stmt.where(Ad.search_text.contains(word, autoescape=True))
    stmt = stmt.order_by(Ad.id.desc()).limit(limit)
    async with session_maker() as session:
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_user_ads(user_id: int) -> Sequence[Ad]:
    stmt = select(Ad).where(Ad.user_id == user_id).order_by(Ad.id.desc())
    async with session_maker() as session:
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_pending_ads(limit: int = 20) -> Sequence[Ad]:
    """Admin tekshiruvini kutayotgan e'lonlar (eskisidan boshlab)."""
    stmt = select(Ad).where(Ad.status == AdStatus.PENDING).order_by(Ad.id.asc()).limit(limit)
    async with session_maker() as session:
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_stats() -> dict:
    """Admin uchun umumiy statistika."""
    async with session_maker() as session:
        rows = (await session.execute(select(Ad.status, func.count()).group_by(Ad.status))).all()
        users = (await session.execute(select(func.count(func.distinct(Ad.user_id))))).scalar_one()
    counts = {status: count for status, count in rows}
    return {
        "pending": counts.get(AdStatus.PENDING, 0),
        "active": counts.get(AdStatus.ACTIVE, 0),
        "rejected": counts.get(AdStatus.REJECTED, 0),
        "users": users,
    }


async def set_status(ad_id: int, status: str, reason: Optional[str] = None) -> Optional[Ad]:
    """Faqat 'pending' holatdagi e'lonning statusini o'zgartiradi.
    Allaqachon ko'rib chiqilgan bo'lsa None qaytaradi."""
    async with session_maker() as session:
        ad = await session.get(Ad, ad_id)
        if ad is None or ad.status != AdStatus.PENDING:
            return None
        ad.status = status
        ad.reject_reason = reason
        await session.commit()
        await session.refresh(ad)
        return ad


async def delete_ad(ad_id: int, user_id: int) -> bool:
    """E'lonni faqat egasi o'chira oladi."""
    async with session_maker() as session:
        ad = await session.get(Ad, ad_id)
        if ad is None or ad.user_id != user_id:
            return False
        await session.delete(ad)
        await session.commit()
        return True