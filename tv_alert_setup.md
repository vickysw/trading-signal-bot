# TV Alert Setup — S2 Zone Pyramid v3 + ICT ChoCH Signal

## How it works

Both indicators use `alert()` internally. TV fires the webhook automatically.
Message format (sent by Pine, no manual editing needed):
```
S2_PASSPHRASE   | XAUUSD | SHORT | Entry:4450.26 SL:4451.46 Lots:0.5 [Normal]
CHOCH_PASSPHRASE | XAUUSD | SHORT | Entry:4450.26 SL:4451.46 Lots:0.021
```

---

## Step 1: Set passphrases in indicators

**S2 Zone Pyramid v3** (Manku-S2-ZonePyramid_v3_DistanceFilter.pine):
- Settings ⚙ → Group "5. Alerts" → Webhook Passphrase → enter your `S2_PASSPHRASE` value

**ICT ChoCH Signal** (ICT-ChoCH-Signal.pine):
- Settings ⚙ → Group "5. Alerts" → Webhook Passphrase → enter your `CHOCH_PASSPHRASE` value

Same values must be in your `.env` file on EC2.

---

## Step 2: Create TV Alerts (do this for EACH indicator)

1. Open indicator on chart
2. Right-click indicator name → "Add alert" (or clock icon)
3. **Condition:** select indicator name → **"Any alert() function call"**
4. **Webhook URL:** `http://YOUR_EC2_PUBLIC_IP:8000/webhook`
5. **Message:** leave empty (indicator sends its own message)
6. **Trigger:** On Bar Close
7. Save

Repeat for the other indicator.

---

## Step 3: Test with curl (from any terminal)

```bash
# Test S2 signal
curl -X POST http://YOUR_EC2_IP:8000/webhook \
  -H "Content-Type: text/plain" \
  -d "YOUR_S2_PASSPHRASE | XAUUSD | SHORT | Entry:4450.26 SL:4451.46 Lots:0.5 [Normal]"

# Test ChoCH signal
curl -X POST http://YOUR_EC2_IP:8000/webhook \
  -H "Content-Type: text/plain" \
  -d "YOUR_CHOCH_PASSPHRASE | XAUUSD | SHORT | Entry:4450.26 SL:4451.46 Lots:0.021"
```

Both should send Telegram messages immediately.

---

## Step 4: Verify server logs

SSH into EC2:
```bash
screen -r signalbot
```
You should see:
```
INFO  Incoming: YOUR_PASS | XAUUSD | SHORT | ...
INFO  Telegram message sent OK
INFO  Signal processed: s2 SHORT 4450.26 XAUUSD
```
