"""SQLAlchemy modellari."""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AdStatus:
    PENDING = "pending"    # admin tekshiruvini kutmoqda
    ACTIVE = "active"      # tasdiqlangan, qidiruvda ko'rinadi
    REJECTED = "rejected"  # rad etilgan


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    photo_id: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(32))
    receipt_id: Mapped[str] = mapped_column(String(255))

    # Kichik harflarga o'tkazilgan "nom + tavsif" — qidiruv uchun
    # (SQLite LIKE faqat lotin harflarda registrga befarq, shuning uchun alohida ustun)
    search_text: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(16), default=AdStatus.PENDING, index=True)
    reject_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())