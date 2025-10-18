#!/bin/bash
echo " Installation du Bot AI TLS..."

apt update && apt upgrade -y
apt install -y python3-pip python3-venv git wget unzip

apt install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-fra

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb

mkdir -p /opt/tls-bot
cd /opt/tls-bot
python3 -m venv venv
source venv/bin/activate

pip install selenium==4.15.0 undetected-chromedriver==3.5.3
pip install webdriver-manager==4.0.1 requests==2.31.0 python-dotenv==1.0.0
pip install opencv-python==4.8.1.78 pytesseract==0.3.10 Pillow==10.0.1 numpy==1.24.3

cat > /etc/systemd/system/tls-bot.service << EOF
[Unit]
Description=Bot AI TLScontact Réservation Automatique
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

echo "✅ Bot AI TLS installé et en fonctionnement !"
echo " Vérifier le statut: systemctl status tls-bot.service"
echo " Voir les logs: journalctl -u tls-bot.service -f"
