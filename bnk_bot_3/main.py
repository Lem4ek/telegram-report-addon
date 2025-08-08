
import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from parser import parse_message
from data_utils import save_entry, generate_stats, get_csv_file
from datetime import datetime, timedelta
from openpyxl import load_workbook
from pathlib import Path
import os
import matplotlib.pyplot as plt
import pandas as pd

TOKEN = os.getenv("TELEGRAM_TOKEN")

ALLOWED_USERS = [1198365511, 508532161]  # замени на свои ID
user_stats = {}
current_month = datetime.now().month
pending_updates = {}

SAVE_DELAY = timedelta(minutes=2)  # тестовая задержка 2 минуты

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def is_allowed(update):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    return username in ALLOWED_USERS or user_id in ALLOWED_USERS

def load_stats_from_excel():
    file_path = get_csv_file()
    if not os.path.exists(file_path):
        return

    wb = load_workbook(file_path)
    ws = wb.active

    for row in ws.iter_rows(min_row=2, values_only=True):
        date, user, pakov, ves, paket, flexa, extru, itogo = row
        if not user:
            continue
        if user not in user_stats:
            user_stats[user] = {
                'Паков': 0.0, 'Вес': 0.0, 'Пакетосварка': 0.0,
                'Флекса': 0.0, 'Экструзия': 0.0, 'Итого': 0.0, 'Смен': 0
            }
        else:
            user_stats[user].setdefault("Смен", 0)

        user_stats[user]['Паков'] += safe_float(pakov)
        user_stats[user]['Вес'] += safe_float(ves)
        user_stats[user]['Пакетосварка'] += safe_float(paket)
        user_stats[user]['Флекса'] += safe_float(flexa)
        user_stats[user]['Экструзия'] += safe_float(extru)
        user_stats[user]['Итого'] += safe_float(itogo)
        user_stats[user]['Смен'] += 1

async def cmd_import(update, context):
    if not is_allowed(update):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⛔ Нет доступа.")
        return

    if not update.message.document:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="📄 Пожалуйста, отправьте Excel-файл.")
        return

    # Удалим текущий Excel-файл и сбросим статистику
    current_file = Path(get_csv_file())
    if current_file.exists():
        current_file.unlink()
        user_stats.clear()

    file = await update.message.document.get_file()
    file_path = f"/tmp/imported.xlsx"
    await file.download_to_drive(file_path)

    try:
        wb = load_workbook(file_path)
        ws = wb.active
        imported = 0

        for row in ws.iter_rows(min_row=2, values_only=True):
            date_str, user, pakov, ves, paket, flexa, extru, itogo = row
            if not user:
                continue

            try:
                if isinstance(date_str, str):
                    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                else:
                    date = date_str
            except Exception:
                date = datetime.now()

            values = {
                "Паков": pakov or 0,
                "Вес": ves or 0,
                "Пакетосварка": paket or 0,
                "Флекса": flexa or 0,
                "Экструзия": extru or 0,
                "Итого": itogo or 0
            }

            save_entry(date, user, values)

            if user not in user_stats:
                user_stats[user] = {
                    'Паков': 0.0, 'Вес': 0.0, 'Пакетосварка': 0.0,
                    'Флекса': 0.0, 'Экструзия': 0.0, 'Итого': 0.0, 'Смен': 0
                }

            user_stats[user]['Паков'] += values["Паков"]
            user_stats[user]['Вес'] += values["Вес"]
            user_stats[user]['Пакетосварка'] += values["Пакетосварка"]
            user_stats[user]['Флекса'] += values["Флекса"]
            user_stats[user]['Экструзия'] += values["Экструзия"]
            user_stats[user]['Итого'] += values["Итого"]
            user_stats[user]['Смен'] += 1

            imported += 1

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"✅ Импорт завершён. Загружено и сохранено записей: {imported}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"❌ Ошибка при импорте: {e}")

# ... (весь остальной main.py должен идти ниже, как у тебя уже есть)
