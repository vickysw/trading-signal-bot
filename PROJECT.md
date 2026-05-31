# S2 Zone Pyramid + ICT ChoCH — Live Signal Alert Bot

## What it does

Automated trading signal delivery system. TradingView indicators fire alerts on bar close → webhook server parses signal → formatted Telegram message sent to subscribers instantly.

Supports two independent strategies running simultaneously:
- **S2 Zone Pyramid v3** — supply/demand zone entries with distance filter (73.7% WR, XAU/USD 5M)
- **ICT ChoCH Signal** — Change of Character macro trend reversal entries (48.9% WR, PF 1.91, XAU/USD 5M)

## Architecture

```
TradingView Alert (bar close)
        ↓
POST /webhook  (EC2 t3.micro, port 80)
        ↓
Parse signal: PASSPHRASE | TICKER | DIRECTION | Entry:X SL:X Lots:X
        ↓
Validate passphrase → identify signal type
        ↓
Calculate T1 (1.5R) + T2 (2.0R) targets
        ↓
Format Telegram message (HTML)
        ↓
Telegram Bot API → Subscriber Channel
```

## Tech Stack

| Layer | Tool |
|---|---|
| Signal source | TradingView Pine Script v6 |
| Webhook server | Python + FastAPI + Uvicorn |
| Hosting | AWS EC2 t3.micro (Ubuntu 22.04) |
| Messaging | Telegram Bot API |
| Process manager | GNU Screen |

## Pine Script Indicators

### S2 Zone Pyramid v3
- HTF dead zone filter (dist ≥ 10pts from 60M EMA50)
- HTF slope visual (aligned = bright, against = dim)
- Position sizing: `Lots = (account × risk%) ÷ (SL_dist × point_val)`
- Alert format: `S2PASS | XAUUSD | SHORT | Entry:4450.26 SL:4451.46 Lots:0.5 [Normal]`

### ICT ChoCH Signal
- Macro trend via HH+HL / LH+LL pivot structure
- Bearish ChoCH: uptrend breaks below last Higher Low
- Bullish ChoCH: downtrend breaks above last Lower High
- Dead zone filter: skip SL distance 5–8pts (spread kills R:R)
- Alert format: `CHOCHPASS | XAUUSD | SHORT | Entry:2345.67 SL:2351.20 Lots:0.021`

## Backtest Results

| Strategy | Timeframe | Trades | Win Rate | Profit Factor | Max DD | Monthly |
|---|---|---|---|---|---|---|
| S2 Zone Pyramid v3 | XAU/USD 5M | 19 | 73.7% | — | — | — |
| ICT ChoCH | XAU/USD 5M | 1,252 | 48.9% | 1.91 | 5.9% | +$1,222 |

*Backtest: Python, 24 months May 2024–May 2026, fixed $5,000 account @ 1% risk*

## Telegram Message Format

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

## Security

- Per-indicator passphrase validation (unknown passphrase → HTTP 403)
- Signals rejected if passphrase missing or mismatched
- EC2 security group: port 80 (webhook) + port 22 (SSH from owner IP only)

## Files

```
signal_bot/
├── main.py              FastAPI webhook server
├── requirements.txt     Dependencies
├── .env.example         Config template
├── setup_ec2.sh         EC2 one-time setup script
└── tv_alert_setup.md    TradingView alert configuration guide
```
