
import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from utils import extract_data, append_to_csv, get_stats, export_csv, reset_all_data
import logging

logging.basicConfig(level=logging.INFO)

token = os.getenv("TELEGRAM_TOKEN")
if not token:
    raise ValueError("TELEGRAM_TOKEN is required in config")

app = ApplicationBuilder().token(token).build()

async def handle_message(update, context):
    user = update.effective_user.first_name
    parsed = extract_data(update.message.text)
    append_to_csv("config/bnk_bot/data/data.csv", user, parsed)
    await update.message.reply_text("✅ Принято!")

async def send_stats(update, context):
    stats = get_stats("config/bnk_bot/data/data.csv")
    await update.message.reply_text(stats)

async def send_csv(update, context):
    await export_csv(update, context, "config/bnk_bot/data/data.csv")

async def reset_data(update, context):
    reset_all_data("config/bnk_bot/data/data.csv")
    await update.message.reply_text("♻️ Данные сброшены")

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CommandHandler("stats", send_stats))
app.add_handler(CommandHandler("csv", send_csv))
app.add_handler(CommandHandler(["reset", "сброс"], reset_data))

app.run_polling()
