#!/usr/bin/env bash
set -euo pipefail

# Читаем опции из /data/options.json (HA сам кладёт туда значения из UI)
export TELEGRAM_TOKEN="$(jq -r '(.TELEGRAM_TOKEN // "")' /data/options.json)"
export ALLOWED_USER_IDS="$(jq -r '(.ALLOWED_USER_IDS // "")' /data/options.json)"

exec python3 -u /app/main.py
