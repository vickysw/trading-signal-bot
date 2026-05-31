"""
S2 Zone Pyramid + ICT ChoCH — Signal Alert Bot
TV Webhook → Parse → Telegram Channel

Setup:
  pip install -r requirements.txt
  cp .env.example .env  (fill your values)
  python main.py

TV Alert message format (both indicators):
  "S2PASS   | XAUUSD | SHORT | Entry:4450.26 SL:4451.46 Lots:0.5 [Normal]"
  "CHOCHPASS | XAUUSD | SHORT | Entry:4450.26 SL:4451.46 Lots:0.021"
  Format: PASSPHRASE | TICKER | DIRECTION | Entry:X SL:X Lots:X [OptionalMode]
"""

import os, re, logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN        = os.environ["TELEGRAM_BOT_TOKEN"]    # from BotFather
CHAT_ID          = os.environ["TELEGRAM_CHAT_ID"]      # channel: -100xxxxxxxxx
S2_PASSPHRASE    = os.environ["S2_PASSPHRASE"]         # must match Pine indicator setting
CHOCH_PASSPHRASE = os.environ["CHOCH_PASSPHRASE"]      # must match Pine indicator setting

KNOWN_PASSPHRASES = {
    S2_PASSPHRASE:    "s2",
    CHOCH_PASSPHRASE: "choch",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(title="S2 + ChoCH Signal Bot")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ── Unified signal parser ──────────────────────────────────────────────────────
def parse_body(body: str) -> dict | None:
    """
    Parse structured TV alert:
    "PASSPHRASE | TICKER | DIRECTION | Entry:X SL:X Lots:X [Mode?]"

    Returns dict with type, ticker, direction, entry, sl, dist, lots, t1, t2, mode
    Returns None if passphrase invalid or format unrecognised.
    """
    parts = [p.strip() for p in body.split(" | ")]
    if len(parts) < 4:
        return None

    passphrase_in = parts[0]
    signal_type   = KNOWN_PASSPHRASES.get(passphrase_in)
    if not signal_type:
        log.warning(f"Unknown passphrase: {passphrase_in!r}")
        return None

    ticker    = parts[1].upper()
    direction = parts[2].upper()
    fields    = parts[3]

    if direction not in ("SHORT", "LONG"):
        return None

    entry_m = re.search(r"Entry:([\d.]+)", fields)
    sl_m    = re.search(r"SL:([\d.]+)",    fields)
    lots_m  = re.search(r"Lots:([\d.]+)",  fields)
    mode_m  = re.search(r"\[(.*?)\]",      fields)

    if not (entry_m and sl_m):
        return None

    entry_p = float(entry_m.group(1))
    sl_p    = float(sl_m.group(1))
    lots_v  = float(lots_m.group(1)) if lots_m else 0.0
    mode_v  = mode_m.group(1) if mode_m else "Normal"

    if direction == "SHORT":
        dist = round(sl_p - entry_p, 2)
        t1   = round(entry_p - dist * 1.5, 2)
        t2   = round(entry_p - dist * 2.0, 2)
    else:
        dist = round(entry_p - sl_p, 2)
        t1   = round(entry_p + dist * 1.5, 2)
        t2   = round(entry_p + dist * 2.0, 2)

    return {
        "type":      signal_type,
        "ticker":    ticker,
        "direction": direction,
        "entry":     entry_p,
        "sl":        sl_p,
        "dist":      dist,
        "lots":      lots_v,
        "t1":        t1,
        "t2":        t2,
        "mode":      mode_v,
    }

# ── Telegram formatters ────────────────────────────────────────────────────────
def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%d %b %Y  %H:%M UTC")

def format_s2_message(sig: dict) -> str:
    d    = sig["direction"]
    e    = sig["entry"]
    sl   = sig["sl"]
    t1   = sig["t1"]
    t2   = sig["t2"]
    lo   = sig["lots"]
    dist = sig["dist"]
    mode = sig["mode"]
    tk   = f" — {sig['ticker']}" if sig["ticker"] else ""

    emoji  = "🔴" if d == "SHORT" else "🟢"
    action = "SHORT ↓" if d == "SHORT" else "LONG ↑"

    return (
        f"{emoji} <b>{action}{tk}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 Entry : <code>{e}</code>\n"
        f"🛑 SL    : <code>{sl}</code>  ({dist} pts)\n"
        f"📦 Lots  : <code>{lo}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 T1    : <code>{t1}</code>  (+1.5R)\n"
        f"🏆 T2    : <code>{t2}</code>  (+2R)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Mode  : {mode}\n"
        f"🕐 {_ts()}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>S2 Zone Pyramid v3</i>"
    )

def format_choch_message(sig: dict) -> str:
    d    = sig["direction"]
    e    = sig["entry"]
    sl   = sig["sl"]
    t1   = sig["t1"]
    t2   = sig["t2"]
    lo   = sig["lots"]
    dist = sig["dist"]
    tk   = f" — {sig['ticker']}" if sig["ticker"] else ""

    emoji  = "🔴" if d == "SHORT" else "🟢"
    action = "SHORT ↓" if d == "SHORT" else "LONG ↑"

    return (
        f"{emoji} <b>ChoCH {action}{tk}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 Entry : <code>{e}</code>\n"
        f"🛑 SL    : <code>{sl}</code>  ({dist} pts)\n"
        f"📦 Lots  : <code>{lo}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 T1    : <code>{t1}</code>  (+1.5R)\n"
        f"🏆 T2    : <code>{t2}</code>  (+2R)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {_ts()}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>ICT ChoCH Signal</i>"
    )

FORMATTERS = {
    "s2":    format_s2_message,
    "choch": format_choch_message,
}

# ── Send to Telegram ───────────────────────────────────────────────────────────
async def send_telegram(text: str):
    payload = {
        "chat_id":    CHAT_ID,
        "text":       text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(TELEGRAM_URL, json=payload)
        if resp.status_code != 200:
            log.error(f"Telegram error: {resp.status_code} {resp.text}")
        else:
            log.info("Telegram message sent OK")
        return resp

# ── Webhook endpoint ───────────────────────────────────────────────────────────
@app.post("/webhook")
async def webhook(request: Request):
    body = (await request.body()).decode("utf-8").strip()
    log.info(f"Incoming: {body[:200]}")

    sig = parse_body(body)
    if not sig:
        log.warning(f"Rejected — invalid passphrase or bad format: {body[:200]}")
        raise HTTPException(status_code=403, detail="forbidden")

    msg = FORMATTERS[sig["type"]](sig)
    await send_telegram(msg)
    log.info(f"Signal processed: {sig['type']} {sig['direction']} {sig['entry']} {sig['ticker']}")
    return JSONResponse({"status": "ok", "signal": sig})

# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/")
async def health():
    return {"status": "running", "bot": "S2 + ChoCH Signal Bot v2"}

@app.get("/ping")
async def ping():
    return {"pong": True}

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
