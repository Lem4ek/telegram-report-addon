#!/bin/bash
chmod -R 755 /app

TELEGRAM_TOKEN=$(cat /data/options.json | grep TELEGRAM_TOKEN | cut -d '"' -f4)

export TELEGRAM_TOKEN
python3 /app/main.py
