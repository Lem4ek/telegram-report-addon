#!/bin/bash
export TELEGRAM_TOKEN=$(jq -r '.TELEGRAM_TOKEN' /data/options.json)
export ALLOWED_USER_IDS="$(bashio::config 'ALLOWED_USER_IDS')"
python3 /app/main.py
