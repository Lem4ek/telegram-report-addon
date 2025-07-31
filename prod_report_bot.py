import os
import datetime
import csv
import re
import matplotlib.pyplot as plt
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8336432137:AAHAn_rsQnj4LghrgWEV7Xc7ZZrle-MMfmQ"
DATA_FILE = "report_log.csv"
PLOT_FILE = "report_plot.png"
data = []

def load_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline='') as f:
            return list(csv.DictReader(f))
    return []

def save_row(row):
    write_header = not os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def parse_report(text, user):
    try:
        result = {"user": user, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                  "Паков": 0, "Вес": 0, "Пакетосварка": 0, "Флекса": 0, "Экструзия_м": 0, "Экструзия_т": 0, "Итого": 0}
        lines = text.splitlines()
        for line in lines:
            line = line.strip().lower()
            if line.startswith("паков"):
                result["Паков"] = int(re.findall(r"\d+", line)[0])
            elif line.startswith("вес"):
                result["Вес"] = int(re.findall(r"\d+", line)[0])
            elif "пакетосварка" in line:
                result["Пакетосварка"] = int(re.findall(r"\d+", line)[0])
            elif "флекс" in line:
                result["Флекса"] = int(re.findall(r"\d+", line)[0])
            elif "экструзия" in line:
                m = re.search(r"м(\d+)", line)
                t = re.search(r"т(\d+)", line)
                if m: result["Экструзия_м"] = int(m.group(1))
                if t: result["Экструзия_т"] = int(t.group(1))
            elif line.startswith("итого"):
                result["Итого"] = int(re.findall(r"\d+", line)[0])
        return result
    except:
        return None

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global data
    text = update.message.text
    user = update.message.from_user.username or update.message.from_user.first_name
    parsed = parse_report(text, user)
    if not parsed:
        await update.message.reply_text("⚠️ Не удалось распознать отчёт.")
        return
    data.append(parsed)
    save_row(parsed)
    reply = f"""✅ Принято от {user}:
📦 Паков: {parsed['Паков']}
⚖️ Вес: {parsed['Вес']}
♻️ Отходы:
  🧵 Пакетосварка: {parsed['Пакетосварка']}
  🎨 Флекса: {parsed['Флекса']}
  🏭 Экструзия: м{parsed['Экструзия_м']} т{parsed['Экструзия_т']}
♻️ Итого отходов: {parsed['Итого']}"""
    await update.message.reply_text(reply)

async def main():
    global data
    data = load_history()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
