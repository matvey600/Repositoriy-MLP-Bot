#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/mlpcompanion}"
SERVICE_NAME="${SERVICE_NAME:-mlpcompanion}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root: sudo bash deploy/update_ubuntu.sh"
  exit 1
fi

git -C "$APP_DIR" pull --ff-only
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
systemctl restart "$SERVICE_NAME"
systemctl status "$SERVICE_NAME" --no-pager

