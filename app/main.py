import os
import re
import asyncio
import pandas as pd
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

DATA_FOLDER = "/config/bnk_bot/data"
FILE_NAME = f"{datetime.now().strftime('%Y-%m')}.xlsx"
FILE_PATH = os.path.join(DATA_FOLDER, FILE_NAME)

os.makedirs(DATA_FOLDER, exist_ok=True)

data_columns = ["User", "Дата", "Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого"]

if not os.path.exists(FILE_PATH):
    df = pd.DataFrame(columns=data_columns)
    df.to_excel(FILE_PATH, index=False)

COMMANDS = [
    BotCommand("csv", "📄 Скачать таблицу"),
    BotCommand("reset", "♻️ Сбросить данные"),
    BotCommand("stats", "📊 Показать статистику")
]

def extract_data_from_message(text):
    data = {
        "Паков": 0,
        "Вес": 0,
        "Пакетосварка": 0,
        "Флекса": 0,
        "Экструзия": "",
        "Итого": 0
    }
    for line in text.splitlines():
        if "паков" in line.lower():
            data["Паков"] = int(re.findall(r'\d+', line)[0])
        elif "вес" in line.lower():
            data["Вес"] = int(re.findall(r'\d+', line)[0])
        elif "пакетосварка" in line.lower():
            data["Пакетосварка"] = int(re.findall(r'\d+', line)[0])
        elif "флекс" in line.lower():
            data["Флекса"] = int(re.findall(r'\d+', line)[0])
        elif "экструзия" in line.lower():
            match = re.search(r"м\d+ т\d+", line)
            if match:
                data["Экструзия"] = match.group()
        elif "итого" in line.lower():
            data["Итого"] = int(re.findall(r'\d+', line)[0])
    return data

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.username or user.first_name
    data = extract_data_from_message(update.message.text)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df = pd.read_excel(FILE_PATH)
    df.loc[len(df)] = [user_name, now, data["Паков"], data["Вес"], data["Пакетосварка"], data["Флекса"], data["Экструзия"], data["Итого"]]
    df.to_excel(FILE_PATH, index=False)

    message = [
        f"Принято от {user_name}:",
        f"📦 Паков: {data['Паков']}",
        f"⚖️ Вес: {data['Вес']}",
        f"♻️ Отходы:",
        f"  🧵 Пакетосварка: {data['Пакетосварка']}",
        f"  🎨 Флекса: {data['Флекса']}",
        f"  🏭 Экструзия: {data['Экструзия']}",
        f"♻️ Итого отходов: {data['Итого']}"
    ]
    await update.message.reply_text("\n".join(message))

async def send_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = pd.read_excel(FILE_PATH)
    df = df.copy()
    df["Экструзия"] = df["Экструзия"].str.replace("экструзия", "", case=False, regex=False).str.strip()
    temp_path = FILE_PATH.replace(".xlsx", "_copy.xlsx")
    df.to_excel(temp_path, index=False)
    await update.message.reply_document(document=open(temp_path, "rb"))

async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pd.DataFrame(columns=data_columns).to_excel(FILE_PATH, index=False)
    await update.message.reply_text("Данные сброшены 🧹")

async def send_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = pd.read_excel(FILE_PATH)
    if df.empty:
        await update.message.reply_text("Данных нет.")
        return

    summary = df.groupby("User")[["Паков", "Вес", "Пакетосварка", "Флекса", "Итого"]].sum()
    report_lines = ["📊 Статистика по пользователям:"]
    for user, row in summary.iterrows():
        report_lines.append(f"👤 {user}: 📦{row['Паков']} ⚖️{row['Вес']} 🧵{row['Пакетосварка']} 🎨{row['Флекса']} ♻️{row['Итого']}")
    await update.message.reply_text("\n".join(report_lines))

async def main():
    token = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("csv", send_csv))
    app.add_handler(CommandHandler("reset", reset_data))
    app.add_handler(CommandHandler("stats", send_stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.bot.set_my_commands(COMMANDS)
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
