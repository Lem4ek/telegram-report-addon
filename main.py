import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from utils import extract_data, format_report, append_to_csv, load_users, save_users, get_stats

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is required in config")

data_file = "storage/data.csv"
users_file = "storage/users.json"

users = load_users(users_file)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username or str(update.effective_user.id)
    try:
        parsed = extract_data(update.message.text)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при разборе сообщения: {e}")
        return
    append_to_csv(data_file, user, parsed)
    users[user] = users.get(user, {"product": 0, "waste": 0})
    users[user]["product"] += parsed.get("Итого", 0)
    users[user]["waste"] += parsed.get("Брак", 0)
    save_users(users_file, users)
    await update.message.reply_text(format_report(parsed))

async def send_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(data_file):
        await update.message.reply_document(document=open(data_file, "rb"))
    else:
        await update.message.reply_text("Файл ещё не создан.")

async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    open(data_file, "w").write("")
    users.clear()
    save_users(users_file, users)
    await update.message.reply_text("Данные сброшены.")

async def send_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_stats(users))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("csv", send_csv))
app.add_handler(CommandHandler("reset", reset_data))
app.add_handler(CommandHandler("stats", send_stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()