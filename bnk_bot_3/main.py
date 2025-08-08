import os
from datetime import datetime
from openpyxl import load_workbook
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from parser import parse_message
from data_utils import save_entry, generate_stats, get_csv_file, get_file_path

TOKEN = os.getenv("TELEGRAM_TOKEN")

ALLOWED_USERS = [1198365511, 508532161]  # замени на нужные ID

user_stats = {}
user_days = {}
current_month = datetime.now().month

def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0

def is_allowed(update):
    return update.effective_user.id in ALLOWED_USERS

def load_stats_from_excel():
    path = get_file_path()
    if not os.path.exists(path):
        return

    wb = load_workbook(path)
    ws = wb.active

    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            date_str, username, pakov, ves, paket, flexa, ext, total = row

            if isinstance(date_str, str):
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            else:
                date = date_str

            user_stats.setdefault(username, {
                'Паков': 0.0, 'Вес': 0.0, 'Пакетосварка': 0.0,
                'Флекса': 0.0, 'Экструзия': 0.0, 'Итого': 0.0, 'Смен': 0
            })

            user_stats[username]['Паков']        += safe_float(pakov)
            user_stats[username]['Вес']          += safe_float(ves)
            user_stats[username]['Пакетосварка'] += safe_float(paket)
            user_stats[username]['Флекса']       += safe_float(flexa)
            user_stats[username]['Экструзия']    += safe_float(ext)
            user_stats[username]['Итого']        += safe_float(total)

            user_days.setdefault(username, set()).add(date.date())
        except Exception as e:
            print(f"[ERR] Строка {i}: {e}")

async def handle_message(update, context):
    global current_month

    if not update.message or not update.message.text:
        return

    text = update.message.text
    values = parse_message(text)
    if not values:
        return

    found_keys = sum(1 for v in values.values() if v not in (0, "", None))
    if found_keys < 3:
        return

    now = datetime.now()
    if now.month != current_month:
        user_stats.clear()
        user_days.clear()
        current_month = now.month

    username = update.effective_user.first_name
    values.setdefault("Паков", 0)
    values.setdefault("Вес", 0)
    values.setdefault("Пакетосварка", 0)
    values.setdefault("Флекса", 0)
    values.setdefault("Экструзия", 0)

    values["Итого"] = (
        safe_float(values.get("Пакетосварка", 0)) +
        safe_float(values.get("Флекса", 0)) +
        safe_float(values.get("Экструзия", 0))
    )

    save_entry(now, username, values)

    user_stats.setdefault(username, {
        'Паков': 0.0, 'Вес': 0.0, 'Пакетосварка': 0.0,
        'Флекса': 0.0, 'Экструзия': 0.0, 'Итого': 0.0, 'Смен': 0
    })

    user_days.setdefault(username, set()).add(now.date())

    for k in values:
        if k in user_stats[username]:
            user_stats[username][k] += safe_float(values[k])

    total_pakov = sum(user['Паков'] for user in user_stats.values())
    total_ves = sum(user['Вес'] for user in user_stats.values())

    report = f"""
📦 Отчёт за смену:

🧮 Паков: {values['Паков']} шт
⚖️ Вес: {values['Вес']} кг

♻️ Отходы:
🔧 Пакетосварка: {values['Пакетосварка']} кг
🖨️ Флекса: {values['Флекса']} кг
🧵 Экструзия: {values['Экструзия']} кг

🧾 Итого отходов: {values['Итого']} кг

📊 Всего продукции за период: {int(total_pakov)} паков / {int(total_ves)} кг
"""
    await update.message.reply_text(report.strip())

async def cmd_csv(update, context):
    if not is_allowed(update):
        return
    file_path = get_csv_file()
    await update.message.reply_document(open(file_path, "rb"))

async def cmd_stats(update, context):
    if not is_allowed(update):
        return
    lines = ["📊 Статистика по сменам:"]
    for user, days in user_days.items():
        lines.append(f"👤 {user}: {len(days)} смен")
    await update.message.reply_text("\n".join(lines))

async def cmd_reset(update, context):
    if not is_allowed(update):
        return
    user_stats.clear()
    user_days.clear()
    await update.message.reply_text("♻️ Статистика сброшена!")

async def cmd_myid(update, context):
    if update.message.chat.type != "private":
        await update.message.reply_text("ℹ️ Напишите команду в личку боту.")
        return
    user_id = update.effective_user.id
    await update.message.reply_text(f"🆔 Ваш ID: `{user_id}`", parse_mode="Markdown")

def main():
    load_stats_from_excel()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("csv", cmd_csv))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.run_polling()

if __name__ == "__main__":
    main()
