"""
QADAM FastAPI — asosiy ilova.
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from backend.db import init_db, SessionLocal, engine
from backend.api.diagnostic import router as diagnostic_router
from backend.api.payments import router as payments_router
from backend.api.admin import router as admin_router
from backend.logger import setup_logging, log

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("app_startup", extra={"action": "startup"})
    try:
        await init_db()
        log.info("db_initialized")
    except Exception as e:
        log.error(f"db_init_failed: {e}")
    yield
    log.info("app_shutdown")


app = FastAPI(title="QADAM API", version="1.0.0", lifespan=lifespan)

ALLOWED = os.getenv("ALLOWED_ORIGINS", "").split(",")
ALLOWED = [o.strip() for o in ALLOWED if o.strip()]

if not ALLOWED:
    ALLOWED = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(diagnostic_router)
app.include_router(payments_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {"service": "Qadam.io", "status": "ok"}


@app.get("/health")
async def health():
    db_ok = False
    try:
        async with SessionLocal() as s:
            await s.execute(select(1))
            db_ok = True
    except Exception:
        pass
    return {
        "ok": db_ok,
        "service": "qadam-io-backend",
        "db": db_ok,
        "ts": datetime.now(timezone.utc).isoformat(),
    }