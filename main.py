import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import calendar
from utils import extract_data, format_report, append_to_csv, load_users, save_users, get_stats, reset_all_data, export_csv

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is required in config")

app = Application.builder().token(TOKEN).build()
scheduler = AsyncIOScheduler()

data_file = "storage/data.csv"
users_file = "storage/users.json"

def monthly_reset():
    today = datetime.today()
    if today.day == calendar.monthrange(today.year, today.month)[1]:
        reset_all_data()

scheduler.add_job(monthly_reset, "cron", hour=23, minute=59)
scheduler.start()

@app.message()
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    parsed = extract_data(update.message.text)
    append_to_csv(data_file, user, parsed)
    save_users(users_file, user, parsed)
    stats = get_stats(users_file)
    await update.message.reply_text(format_report(parsed, stats))

@app.command("csv")
async def send_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(data_file):
        await update.message.reply_document(document=open(data_file, "rb"))
    else:
        await update.message.reply_text("Файл пуст или не найден.")

@app.command("сброс")
async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_all_data()
    await update.message.reply_text("Данные сброшены.")

app.run_polling()