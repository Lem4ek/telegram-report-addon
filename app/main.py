import os
import asyncio
import pandas as pd
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

DATA_FOLDER = "data"
EXCEL_FILE = os.path.join(DATA_FOLDER, f"report_{datetime.now().strftime('%Y_%m')}.xlsx")
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

columns = ["Пользователь", "Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого"]
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=columns)
    df.to_excel(EXCEL_FILE, index=False)

def extract_data(text):
    data = {"Паков": 0, "Вес": 0, "Пакетосварка": 0, "Флекса": 0, "Экструзия": "", "Итого": 0}
    lines = text.splitlines()
    for line in lines:
        l = line.lower()
        if "паков" in l:
            data["Паков"] = int("".join(filter(str.isdigit, line)))
        elif "вес" in l:
            data["Вес"] = int("".join(filter(str.isdigit, line)))
        elif "пакетосварка" in l:
            data["Пакетосварка"] = int("".join(filter(str.isdigit, line)))
        elif "флекс" in l:
            data["Флекса"] = int("".join(filter(str.isdigit, line)))
        elif "экструзия" in l:
            data["Экструзия"] = line.replace("Экструзия", "").strip()
        elif "итого" in l:
            data["Итого"] = int("".join(filter(str.isdigit, line)))
    return data

def save_data(user: str, data: dict):
    df = pd.read_excel(EXCEL_FILE)
    row = {
        "Пользователь": user,
        "Паков": data["Паков"],
        "Вес": data["Вес"],
        "Пакетосварка": data["Пакетосварка"],
        "Флекса": data["Флекса"],
        "Экструзия": data["Экструзия"],
        "Итого": data["Итого"],
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

def generate_stats():
    df = pd.read_excel(EXCEL_FILE)
    if df.empty:
        return "Нет данных."
    stats = df.groupby("Пользователь")[["Паков", "Вес", "Пакетосварка", "Флекса", "Итого"]].sum()
    msg = "\ud83c\udf09 <b>\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f\u043c:</b>\n"
    for user, row in stats.iterrows():
        msg += f"\n<b>{user}</b>\n📦 {row['Паков']} | ⚖️ {row['Вес']} | 🧵 {row['Пакетосварка']} | 🎨 {row['Флекса']} | ♻️ {row['Итого']}"
    return msg

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    data = extract_data(update.message.text)
    save_data(user_name, data)
    response_text = (
        f"Принято от {user_name}:\n"
        f"📦 Паков: {data['Паков']}\n"
        f"⚖️ Вес: {data['Вес']}\n"
        f"♻️ Отходы:\n"
        f"  🧵 Пакетосварка: {data['Пакетосварка']}\n"
        f"  🎨 Флекса: {data['Флекса']}\n"
        f"  🏭 {data['Экструзия']}\n"
        f"♻️ Итого отходов: {data['Итого']}"
    )
    await update.message.reply_text(response_text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = generate_stats()
    await update.message.reply_html(msg)

async def csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_document(document=open(EXCEL_FILE, "rb"))

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = pd.DataFrame(columns=columns)
    df.to_excel(EXCEL_FILE, index=False)
    await update.message.reply_text("Данные сброшены")

async def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN env variable is required")

    app = ApplicationBuilder().token(token).build()

    bot_commands = [
        BotCommand("stats", "📊 Показать статистику"),
        BotCommand("csv", "📎 Скачать Excel-файл"),
        BotCommand("reset", "🧹 Сброс данных")
    ]
    await app.bot.set_my_commands(bot_commands)

    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("csv", csv))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    import nest_asyncio
    nest_asyncio.apply()
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
