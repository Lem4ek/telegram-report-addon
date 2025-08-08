import os
from datetime import datetime
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from parser import parse_message
from data_utils import save_entry, get_csv_file, generate_stats
from openpyxl import load_workbook

TOKEN = os.getenv("TELEGRAM_TOKEN")

user_stats = {}
user_days = {}
current_month = datetime.now().month

ALLOWED_USERS = [1198365511, 508532161]  # замени на свои Telegram ID

def safe_int(v):
    try:
        return int(v)
    except:
        return 0

def safe_float(v):
    try:
        return float(str(v).replace(",", "."))
    except:
        return 0.0

def is_allowed(update):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    return user_id in ALLOWED_USERS or username in ALLOWED_USERS

def load_stats_from_excel():
    file_path = get_csv_file()
    if not os.path.exists(file_path):
        return

    from datetime import datetime
    wb = load_workbook(file_path, data_only=True)
    ws = wb.active

    for row in ws.iter_rows(min_row=2, values_only=True):
        date, user, pakov, ves, paket, flexa, extru, itogo = row
        if not user or not date:
            continue

        username = str(user)
        user_stats.setdefault(username, {
            'Паков': 0.0, 'Вес': 0.0, 'Пакетосварка': 0.0, 'Флекса': 0.0,
            'Экструзия': 0.0, 'Итого': 0.0, 'Смен': 0
        })
        user_days.setdefault(username, set())
        user_days[username].add(date.date())

        user_stats[username]['Паков'] += safe_float(pakov)
        user_stats[username]['Вес'] += safe_float(ves)
        user_stats[username]['Пакетосварка'] += safe_float(paket)
        user_stats[username]['Флекса'] += safe_float(flexa)
        user_stats[username]['Экструзия'] += safe_float(extru)
        user_stats[username]['Итого'] += safe_float(itogo)

    for username, days in user_days.items():
        user_stats[username]['Смен'] = len(days)

async def handle_message(update, context):
    global current_month

    if not update.message or not update.message.text:
        return

    username = update.effective_user.first_name
    text = update.message.text
    values = parse_message(text)

    if not values:
        return

    # Проверка количества ключей
    if sum(1 for v in values.values() if v not in (0, "", None)) < 3:
        return

    # Авто-сброс статистики в начале нового месяца
    month_now = datetime.now().month
    if month_now != current_month:
        user_stats.clear()
        user_days.clear()
        current_month = month_now

    # Подготовка данных
    for key in ["Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия"]:
        values.setdefault(key, 0)

    pak = safe_float(values.get("Пакетосварка", 0))
    fle = safe_float(values.get("Флекса", 0))
    ext = safe_float(values.get("Экструзия", 0))
    values["Итого"] = pak + fle + ext

    save_entry(datetime.now(), username, values)

    user_stats.setdefault(username, {
        'Паков': 0, 'Вес': 0,
        'Пакетосварка': 0, 'Флекса': 0, 'Экструзия': 0, 'Итого': 0, 'Смен': 0
    })
    for k in values:
        if k in user_stats[username]:
            user_stats[username][k] += values[k]

    # Учёт смен
    user_days.setdefault(username, set())
    user_days[username].add(datetime.now().date())
    user_stats[username]['Смен'] = len(user_days[username])

    total_pakov_all = sum(u['Паков'] for u in user_stats.values())
    total_ves_all = sum(u['Вес'] for u in user_stats.values())
    shifts_cnt = int(user_stats[username].get('Смен', 0))

    report = f"""
📦 Отчёт за смену:

🧮 Паков: {values['Паков']} шт
⚖️ Вес: {values['Вес']} кг

♻️ Отходы:
🔧 Пакетосварка: {pak} кг
🖨️ Флекса: {fle} кг
🧵 Экструзия: {ext} кг

🧾 Итого отходов: {values['Итого']} кг

👤 Пользователь: {username}
🗓 Смен в этом месяце: {shifts_cnt}

📊 Всего продукции за период: {total_pakov_all} паков / {total_ves_all} кг
"""
    await update.message.reply_text(report.strip())

async def cmd_stats(update, context):
    if not is_allowed(update):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    await update.message.reply_text(generate_stats(user_stats))

async def cmd_csv(update, context):
    if not is_allowed(update):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    file_path = get_csv_file()
    await update.message.reply_document(open(file_path, 'rb'))

async def cmd_reset(update, context):
    if not is_allowed(update):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    user_stats.clear()
    user_days.clear()
    await update.message.reply_text("♻️ Статистика сброшена!")

async def cmd_myid(update, context):
    if update.message.chat.type != "private":
        await update.message.reply_text("ℹ️ Запросите свой ID в личном чате с ботом.")
        return
    user_id = update.effective_user.id
    await update.message.reply_text(f"🆔 Ваш Telegram ID: `{user_id}`", parse_mode="Markdown")

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN env variable is required")
    
    load_stats_from_excel()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("csv", cmd_csv))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
