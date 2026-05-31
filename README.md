# Trading Signal Bot — TradingView → Telegram

Real-time trading signal delivery. TradingView indicators fire alerts on bar close → FastAPI webhook on AWS EC2 → Telegram channel.

Supports two strategies simultaneously:
- **S2 Zone Pyramid v3** — supply/demand zone entries (73.7% WR, XAU/USD 5M)
- **ICT ChoCH Signal** — macro trend reversal entries (48.9% WR, PF 1.91, 24M backtest)

## Architecture

```
TradingView Alert (bar close)
        ↓
POST /webhook  (AWS EC2, port 80)
        ↓
Validate passphrase → detect signal type
        ↓
Parse: Entry, SL, Lots → compute T1 (1.5R) + T2 (2.0R)
        ↓
Telegram Bot → Subscriber Channel
```

## Telegram Message

```
🔴 ChoCH SHORT ↓ — XAUUSD
━━━━━━━━━━━━━━━━━━━━
📍 Entry : 2345.67
🛑 SL    : 2351.20  (5.53 pts)
📦 Lots  : 0.021
━━━━━━━━━━━━━━━━━━━━
🎯 T1    : 2337.37  (+1.5R)
🏆 T2    : 2334.61  (+2R)
━━━━━━━━━━━━━━━━━━━━
🕐 01 Jun 2026  08:30 UTC
━━━━━━━━━━━━━━━━━━━━
ICT ChoCH Signal
```

## Tech Stack

- **Python** — FastAPI, Uvicorn, httpx, python-dotenv
- **Pine Script v6** — TradingView indicators with built-in alerts
- **AWS EC2** — t3.micro, Ubuntu 22.04
- **Telegram Bot API** — HTML formatted messages

## Setup

```bash
git clone https://github.com/vickysw/trading-signal-bot.git
cd trading-signal-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill .env with your values
python main.py
```

## Environment Variables

```env
TELEGRAM_BOT_TOKEN=     # from @BotFather
TELEGRAM_CHAT_ID=       # channel ID (-100xxxxxxxxx)
S2_PASSPHRASE=          # must match Pine indicator setting
CHOCH_PASSPHRASE=       # must match Pine indicator setting
PORT=80
```

## Signal Format (TradingView → Webhook)

```
S2_PASS   | XAUUSD | SHORT | Entry:4450.26 SL:4451.46 Lots:0.5 [Normal]
CHOCH_PASS | XAUUSD | SHORT | Entry:2345.67 SL:2351.20 Lots:0.021
```

## Backtest Results

| Strategy | Trades | Win Rate | Profit Factor | Max DD | Monthly Profit |
|---|---|---|---|---|---|
| S2 Zone Pyramid v3 | 19 | 73.7% | — | — | — |
| ICT ChoCH | 1,252 | 48.9% | 1.91 | 5.9% | +$1,222 |

*24 months, XAU/USD 5M, $5,000 account @ 1% risk*

## Security

- Per-indicator passphrase — unknown passphrase returns HTTP 403
- `.env` excluded from git (never committed)
