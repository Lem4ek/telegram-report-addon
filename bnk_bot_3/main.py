from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, ContextTypes
from parser import parse_message
from data_utils import save_entry, generate_stats, get_csv_file
from datetime import datetime
import os
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")

user_stats = {}

async def handle_message(update, context):
    if not update.message or not update.message.text:
        return
    username = update.effective_user.first_name
    text = update.message.text
    values = parse_message(text)
    if values:
        save_entry(datetime.now(), username, values)
        user_stats.setdefault(username, {'Паков': 0, 'Вес': 0, 'Пакетосварка': 0, 'Флекса': 0, 'Итого': 0})
        for k in values:
            if k in user_stats[username]:
                user_stats[username][k] += values[k]
        await update.message.reply_text("✅ Данные записаны.")

async def cmd_csv(update, context):
    file_path = get_csv_file()
    await update.message.reply_document(open(file_path, 'rb'))

async def cmd_stats(update, context):
    await update.message.reply_text(generate_stats(user_stats))

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN env variable is required")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("csv", cmd_csv))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
