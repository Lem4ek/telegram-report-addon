import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from utils import extract_data, format_report, append_to_csv, load_users, save_users, get_stats, reset_all_data, export_csv

TOKEN = os.getenv("TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is required in config")

app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот учёта продукции и отходов.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    data = extract_data(text)
    if data:
        append_to_csv(data, user.username or str(user.id))
        save_users(user)
        reply = format_report(data)
        await update.message.reply_text(reply)

async def csv_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filepath = export_csv()
    await update.message.reply_document(document=open(filepath, 'rb'))

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_stats())

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_all_data()
    await update.message.reply_text("Данные сброшены.")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("csv", csv_command))
app.add_handler(CommandHandler("stats", stats_command))
app.add_handler(CommandHandler("сброс", reset_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()