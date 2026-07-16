#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/matvey600/Repositoriy-MLP-Bot.git}"
APP_DIR="${APP_DIR:-/opt/mlpcompanion}"
SERVICE_USER="${SERVICE_USER:-mlpcompanion}"
SERVICE_NAME="${SERVICE_NAME:-mlpcompanion}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root: sudo bash deploy/install_ubuntu.sh"
  exit 1
fi

apt-get update
apt-get install -y git python3 python3-venv python3-pip

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  useradd --system --create-home --shell /usr/sbin/nologin "$SERVICE_USER"
fi

if [ ! -d "$APP_DIR/.git" ]; then
  mkdir -p "$APP_DIR"
  git clone "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" pull --ff-only
fi

python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

if [ ! -f "$APP_DIR/.env" ]; then
  cp "$APP_DIR/.env.example" "$APP_DIR/.env"
  chmod 600 "$APP_DIR/.env"
  echo "Created $APP_DIR/.env. Fill BOT_TOKEN and GEMINI_API_KEY before starting the bot."
fi

chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"

cat > "/etc/systemd/system/$SERVICE_NAME.service" <<SERVICE
[Unit]
Description=MLPCompanion Telegram bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$APP_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=$APP_DIR/.venv/bin/python $APP_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

echo
echo "Installed $SERVICE_NAME."
echo "Next steps:"
echo "1. Edit secrets: sudo nano $APP_DIR/.env"
echo "2. Start bot:    sudo systemctl start $SERVICE_NAME"
echo "3. View logs:    sudo journalctl -u $SERVICE_NAME -f"

