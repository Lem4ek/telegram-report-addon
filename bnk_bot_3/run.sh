#!/bin/bash
export TELEGRAM_TOKEN=$(jq -r '.TELEGRAM_TOKEN' /data/options.json)
python3 /app/main.py