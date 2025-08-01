#!/bin/bash
chmod -R 755 /app
TELEGRAM_TOKEN=$(grep TELEGRAM_TOKEN /data/options.json | cut -d '"' -f4)
export TELEGRAM_TOKEN
python3 /app/main.py
