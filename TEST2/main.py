import logging
import os
import json
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from utils import extract_data, format_report, append_to_csv, load_users, save_users, get_stats

# Обеспечиваем наличие директории
os.makedirs("storage", exist_ok=True)

CONFIG_PATH = "/data/options.json"
with open(CONFIG_PATH, "r") as f:
    options = json.load(f)

TOKEN = options.get("telegram_token")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is required in config")

logging.basicConfig(level=logging.INFO)
data_file = "storage/data.csv"
users_file = "storage/users.json"
users = load_users(users_file)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user = update.message.from_user.username or update.message.from_user.first_name
        parsed = extract_data(update.message.text)
        if parsed:
            append_to_csv(data_file, user, parsed)
            users[user] = users.get(user, 0) + 1
            save_users(users_file, users)
            await update.message.reply_text(format_report(parsed))

async def send_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(data_file):
        await update.message.reply_document(InputFile(data_file, filename="data.csv"))

async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    open(data_file, "w").write("Дата,Пользователь,Паков,Вес,Пакетосварка,Флекса,Экструзия,Итого\n")
    save_users(users_file, {})
    await update.message.reply_text("🔄 Data reset.")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_stats(data_file)
    await update.message.reply_text(stats)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("csv", send_csv))
    app.add_handler(CommandHandler("reset", reset_data))
    app.add_handler(CommandHandler("stats", show_stats))
    app.run_polling()