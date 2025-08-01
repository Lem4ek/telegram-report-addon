import os
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from data_utils import save_data, export_excel, reset_month_data, get_user_stats
from parser import extract_report_data

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN env variable is required")

data_file_dir = "/config/bnk_bot/data"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user = update.effective_user
    user_name = user.full_name if user else "Unknown"
    user_id = user.id if user else 0

    parsed_data = extract_report_data(text)
    if parsed_data:
        save_data(parsed_data, user_name, user_id, data_file_dir)
        await update.message.reply_text("✅ Данные добавлены!")
    else:
        await update.message.reply_text("⚠️ Не удалось распознать данные.")

async def cmd_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = export_excel(data_file_dir)
    if file_path:
        await update.message.reply_document(open(file_path, "rb"))
    else:
        await update.message.reply_text("❌ Нет данных за текущий месяц.")

async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_month_data(data_file_dir)
    await update.message.reply_text("♻️ Данные сброшены!")

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_user_stats(data_file_dir)
    await update.message.reply_text(stats)

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CommandHandler("csv", cmd_csv))
app.add_handler(CommandHandler("reset", cmd_reset))
app.add_handler(CommandHandler("stats", cmd_stats))

# Устанавливаем команды
async def set_bot_commands():
    bot_commands = [
        BotCommand("csv", "📁 Получить Excel-файл"),
        BotCommand("reset", "♻️ Сбросить данные"),
        BotCommand("stats", "📊 Показать статистику"),
    ]
    await app.bot.set_my_commands(bot_commands)

# Фоновая задача
app.post_init = set_bot_commands

if __name__ == "__main__":
    app.run_polling()
