#!/bin/bash
# Run on AWS EC2 (Amazon Linux 2 / Ubuntu)
# chmod +x setup_ec2.sh && ./setup_ec2.sh

set -e

echo "=== Installing Python + dependencies ==="
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv git screen

echo "=== Clone / copy your project ==="
# Option A: git clone (if on GitHub)
# git clone https://github.com/yourusername/signal_bot.git
# cd signal_bot

# Option B: already copied via SCP — just cd into it
# cd signal_bot

echo "=== Create virtual environment ==="
python3 -m venv venv
source venv/bin/activate

echo "=== Install packages ==="
pip install -r requirements.txt

echo "=== Setup .env ==="
cp .env.example .env
echo ""
echo "EDIT .env NOW with your values:"
echo "  nano .env"
echo ""

echo "=== Open port 8000 on EC2 ==="
echo "Go to AWS Console → EC2 → Security Groups → Add Inbound Rule:"
echo "  Type: Custom TCP  Port: 8000  Source: 0.0.0.0/0"
echo ""

echo "=== Start server (persistent with screen) ==="
echo "Run these commands after editing .env:"
echo ""
echo "  screen -S signalbot"
echo "  source venv/bin/activate"
echo "  python main.py"
echo "  Ctrl+A then D  (detach — server keeps running)"
echo ""
echo "To reattach: screen -r signalbot"
echo ""
echo "=== Your webhook URL will be ==="
echo "  http://YOUR_EC2_PUBLIC_IP:8000/webhook"
echo ""
echo "=== Done! ==="
