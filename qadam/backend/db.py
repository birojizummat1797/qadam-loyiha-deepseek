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

# QADAM_DB_READ_ONLY=1 (used by the recompute dry-run workflow): every
# transaction is read-only at the PostgreSQL level, so any write fails in the
# database itself, whatever the code tries to do.
READ_ONLY = os.getenv("QADAM_DB_READ_ONLY") == "1"

# SQLite fallback (lokal test uchun)
if DATABASE_URL.startswith("postgresql"):
    connect_args = {"server_settings": {"default_transaction_read_only": "on"}} if READ_ONLY else {}
    engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True, connect_args=connect_args)
else:
    engine = create_async_engine(DATABASE_URL, echo=False)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Jadvallarni yaratish."""
    # Modellarni import qilish (metadata to'lishi uchun)
    from backend import models  # noqa
    from backend import models_v2  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)