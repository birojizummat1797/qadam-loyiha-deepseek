# -*- coding: utf-8 -*-
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("1. .env dagi DATABASE_URL")
print("=" * 60)
url = os.getenv("DATABASE_URL", "TOPILMADI")
print(url)
print()

print("=" * 60)
print("2. URL tekshiruvi")
print("=" * 60)
if url.startswith("postgresql+asyncpg://"):
    print("OK: postgresql+asyncpg:// bilan boshlanadi")
elif url.startswith("postgresql://"):
    print("XATO: postgresql:// bilan boshlanadi (asyncpg kerak)")
elif url.startswith("sqlite"):
    print("XATO: SQLite ishlatilmoqda!")
else:
    print("XATO: URL formati notanish")
print()

print("=" * 60)
print("3. Neon'ga ulanish testi")
print("=" * 60)


async def test():
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text

        engine = create_async_engine(url, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("OK: Neon bilan aloqa ishlayapti")

            result = await conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname='public'"
            ))
            tables = [row[0] for row in result]
            print()
            print("Jadvallar soni:", len(tables))
            for t in tables:
                print("  -", t)

        await engine.dispose()
    except Exception as e:
        print("XATO:", type(e).__name__, "-", str(e)[:200])


asyncio.run(test())