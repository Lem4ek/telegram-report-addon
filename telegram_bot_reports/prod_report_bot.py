from telegram import Update, ChatMember, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import re
import json
import os
from datetime import datetime
from collections import defaultdict
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

HISTORY_FILE = "report_full_history.json"
EXCEL_FILE = "report_log.xlsx"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if update.effective_chat.type in ["group", "supergroup"]:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    return True

async def reset_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("Only an administrator can reset the history.")
        return

    chat_id = str(update.effective_chat.id)
    history = load_history()
    if chat_id in history:
        del history[chat_id]
        save_history(history)
        await update.message.reply_text("History has been reset.")
    else:
        await update.message.reply_text("History was already empty.")

def parse_report(text):
    result = {}
    lines = text.strip().splitlines()
    for line in lines:
        if 'Остаток' in line:
            break
        match = re.match(r"^(\d+)[\s\-:]+(\d+)$", line.strip())
        if match:
            key, value = match.groups()
            result[int(key)] = int(value)
    return result

def aggregate_reports(reports):
    merged = defaultdict(int)
    for report in reports:
        for key, value in report.items():
            merged[int(key)] += int(value)
    return dict(merged)

def append_to_excel(chat_id: str, report: dict, timestamp: str, user: str):
    row = {
        "chat_id": chat_id,
        "timestamp": timestamp,
        "user": user
    }
    row.update({str(k): v for k, v in report.items()})
    df_new = pd.DataFrame([row])

    if os.path.exists(EXCEL_FILE):
        df_existing = pd.read_excel(EXCEL_FILE)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_excel(EXCEL_FILE, index=False)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or update.effective_user.first_name or f"ID:{user_id}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = update.message.text
    current_report = parse_report(text)

    if not current_report:
        return

    history = load_history()
    chat_history = history.get(chat_id, {
        "reports": [],
        "month": datetime.now().month
    })

    if chat_history["month"] != datetime.now().month:
        chat_history = {"reports": [], "month": datetime.now().month}

    chat_history["reports"].append(current_report)
    history[chat_id] = chat_history
    save_history(history)

    append_to_excel(chat_id, current_report, timestamp, username)

    merged = aggregate_reports(chat_history["reports"])
    total_sum = sum(merged.values())

    reply_lines = [f"{k} - {v}" for k, v in sorted(merged.items())]
    reply_lines.append(f"\nИтого: {total_sum}")
    await update.message.reply_text("\n".join(reply_lines))

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(EXCEL_FILE):
        await update.message.reply_text("No data available.")
        return

    try:
        df = pd.read_excel(EXCEL_FILE)
        if "user" not in df.columns:
            await update.message.reply_text("No user data found.")
            return

        numeric_cols = [col for col in df.columns if col.isdigit()]
        if not numeric_cols:
            await update.message.reply_text("No numeric data to show.")
            return

        user_stats = df.groupby("user")[numeric_cols].sum()
        stats_text = "📊 Сводка по пользователям:\n\n"
        for user, row in user_stats.iterrows():
            stats_text += f"{user}:\n"
            for key, val in row.items():
                stats_text += f"  {key} - {val}\n"
            stats_text += "\n"

        await update.message.reply_text(stats_text.strip())

    except Exception as e:
        logging.exception("Error generating statistics:")
        await update.message.reply_text("Ошибка при построении статистики.")

async def excel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("Only an admin can request Excel reports.")
        return

    if os.path.exists(EXCEL_FILE):
        with open(EXCEL_FILE, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename="report_log.xlsx")
            )
    else:
        await update.message.reply_text("Файл отчёта ещё не создан.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Exception while handling an update:", exc_info=context.error)

def main():
    TOKEN = "8336432137:AAHAn_rsQnj4LghrgWEV7Xc7ZZrle-MMfmQ"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("reset", reset_history))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("excel", excel_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
