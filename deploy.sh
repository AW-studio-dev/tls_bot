#!/bin/bash
apt update && apt upgrade -y
apt install -y python3-pip python3-venv git
mkdir -p /opt/tls-bot
cd /opt/tls-bot
python3 -m venv venv
source venv/bin/activate
pip install requests python-dotenv

cat > /etc/systemd/system/tls-bot.service << EOF
[Unit]
Description=TLScontact Auto-Booking Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/tls-bot
Environment=PATH=/opt/tls-bot/venv/bin
ExecStart=/opt/tls-bot/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable tls-bot.service
systemctl start tls-bot.service
