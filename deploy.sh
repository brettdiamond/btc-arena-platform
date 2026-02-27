#!/usr/bin/env bash
set -e

echo "[btc-arena] Starting deploy..."

# 1) Install system packages we need
apt update
apt install -y python3 python3-pip python3-flask

# 2) Create app directory on server
mkdir -p /opt/btc-arena-platform

# 3) Copy repo contents to /opt/btc-arena-platform
# (Assumes you cloned the repo into /opt/btc-arena-platform; this is mostly for updates)
cp -r . /opt/btc-arena-platform/

cd /opt/btc-arena-platform

# 4) Install any Python dependencies via pip if needed (lightweight for now)
pip3 install --break-system-packages flask

# 5) Install/refresh systemd services
cp btc-arena.service /etc/systemd/system/btc-arena.service
cp btc-arena-web.service /etc/systemd/system/btc-arena-web.service

systemctl daemon-reload

# 6) Enable and start services
systemctl enable btc-arena.service
systemctl enable btc-arena-web.service

systemctl restart btc-arena.service || systemctl start btc-arena.service
systemctl restart btc-arena-web.service || systemctl start btc-arena-web.service

echo "[btc-arena] Deploy complete."
