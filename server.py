"""Server: dashboard (/), API (/api/*) va Telegram bot bitta jarayonda.
Ishga tushirish:  uvicorn server:app --host 0.0.0.0 --port 8000"""
import asyncio
import hashlib
import hmac
import json
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import parse_qsl

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Header, HTTPException  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402

from engine import Cfg, Engine  # noqa: E402
from feeds import DemoFeed, DexFeed  # noqa: E402

TOKEN = os.getenv("BOT_TOKEN", "")
OWNER = int(os.getenv("OWNER_ID") or 0)
PUBLIC_URL = os.getenv("PUBLIC_URL", "")
DEMO = os.getenv("DEMO", "0") == "1"
tg = None


async def notify(text):
    if tg and OWNER:
        await tg.bot.send_message(OWNER, text)


eng = Engine(DemoFeed() if DEMO else DexFeed(), Cfg, notify)


def auth(init_data):
    """OWNER_ID berilgan bo'lsa, faqat Telegram Mini App ichidan egasi kira oladi."""
    if not OWNER:
        return  # faqat lokal sinov uchun! Internetga ochishdan oldin OWNER_ID ni kiriting.
    if not init_data or not TOKEN:
        raise HTTPException(401)
    d = dict(parse_qsl(init_data, keep_blank_values=True))
    h = d.pop("hash", "")
    s = "\n".join(f"{k}={v}" for k, v in sorted(d.items()))
    key = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(hmac.new(key, s.encode(), hashlib.sha256).hexdigest(), h):
        raise HTTPException(401)
    if time.time() - int(d.get("auth_date", 0)) > 86400:
        raise HTTPException(401)
    if json.loads(d.get("user", "{}")).get("id") != OWNER:
        raise HTTPException(403)


async def tg_start():
    if not (TOKEN and OWNER):
        return None
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
    from telegram.ext import Application, CommandHandler, filters

    app = Application.builder().token(TOKEN).build()
    only = filters.User(OWNER)

    async def start(u, c):
        kb = None
        if PUBLIC_URL.startswith("https://"):
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("Terminalni ochish", web_app=WebAppInfo(PUBLIC_URL))]])
        await u.message.reply_text("Grok Bot Terminal · paper rejim (soxta pul).", reply_markup=kb)

    async def status(u, c):
        s = eng.state()
        await u.message.reply_text(
            f"Balans ${s['bal']:.2f} · bitimlar {s['tr']} ({s['w']}W/{s['l']}L) · "
            f"{'pauza' if s['paused'] else 'ishlayapti'}")

    async def pause(u, c):
        eng.paused = True
        await u.message.reply_text("Yangi bitim qidirish to‘xtatildi (ochiq pozitsiya baribir nazorat qilinadi).")

    async def resume(u, c):
        eng.paused = False
        await u.message.reply_text("Davom etyapti.")

    for name, fn in (("start", start), ("status", status), ("pause", pause), ("resume", resume)):
        app.add_handler(CommandHandler(name, fn, filters=only))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    return app


@asynccontextmanager
async def lifespan(_):
    global tg
    tg = await tg_start()
    task = asyncio.create_task(eng.run())
    yield
    task.cancel()
    if tg:
        await tg.updater.stop()
        await tg.stop()
        await tg.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index():
    return FileResponse(Path(__file__).parent / "docs" / "index.html")


@app.get("/api/state")
async def state(x_init_data: str | None = Header(None)):
    auth(x_init_data)
    return eng.state()


@app.post("/api/pause")
async def pause(x_init_data: str | None = Header(None)):
    auth(x_init_data)
    eng.paused = not eng.paused
    return {"paused": eng.paused}


@app.post("/api/reset")
async def reset(x_init_data: str | None = Header(None)):
    auth(x_init_data)
    if eng.pos:
        raise HTTPException(409, "ochiq pozitsiya bor")
    eng.reset()
    return {"ok": True}
