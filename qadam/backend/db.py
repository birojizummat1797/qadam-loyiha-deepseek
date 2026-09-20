"""
Database ulanish + Base model.
PostgreSQL (Neon) uchun async engine.
"""
import os
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./qadam.db")

# SQLite fallback (lokal test uchun)
if DATABASE_URL.startswith("postgresql"):
    engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
else:
    engine = create_async_engine(DATABASE_URL, echo=False)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Jadvallarni yaratish."""
    # Modellarni import qilish (metadata to'lishi uchun)
    from backend import models  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)