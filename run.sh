#!/bin/bash
chmod -R 755 /app
export TELEGRAM_TOKEN="$(jq -r '.TELEGRAM_TOKEN' /data/options.json)"
python3 /app/main.py
