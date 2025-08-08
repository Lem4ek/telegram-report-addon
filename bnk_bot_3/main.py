import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from parser import parse_message
from data_utils import save_entry, generate_stats, get_csv_file
from datetime import datetime
from collections import defaultdict

TOKEN = os.getenv("TELEGRAM_TOKEN")

# Разрешённые пользователи (Telegram ID)
ALLOWED_USERS = [1198365511, 508532161]

# Статистика пользователей
user_stats = {}
user_days = defaultdict(set)
current_month = datetime.now().month

# Проверка, разрешён ли пользователь
def is_allowed(update):
    user_id = update.effective_user.id
    return user_id in ALLOWED_USERS

# Безопасное приведение к числу
def safe_number(value):
    try:
        return float(value)
    except:
        return 0

# Основной обработчик сообщений
async def handle_message(update, context):
    global current_month

    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    if "вес" not in text and "итого" not in text:
        return  # фильтруем сообщения с количеством людей, а не отчёты

    now = datetime.now()
    if now.month != current_month:
        user_stats.clear()
        user_days.clear()
        current_month = now.month

    username = update.effective_user.first_name
    parsed = parse_message(update.message.text)

    if not parsed:
        return

    # Приведение значений
    pakov = safe_number(parsed.get("Паков", 0))
    ves = safe_number(parsed.get("Вес", 0))
    pak = safe_number(parsed.get("Пакетосварка", 0))
    fle = safe_number(parsed.get("Флекса", 0))
    ext = safe_number(parsed.get("Экструзия", 0))
    total = pak + fle + ext

    parsed["Паков"] = pakov
    parsed["Вес"] = ves
    parsed["Пакетосварка"] = pak
    parsed["Флекса"] = fle
    parsed["Экструзия"] = ext
    parsed["Итого"] = total

    # Сохраняем в Excel
    save_entry(now, username, parsed)

    # Обновляем статистику
    if username not in user_stats:
        user_stats[username] = {
            "Паков": 0, "Вес": 0, "Пакетосварка": 0,
            "Флекса": 0, "Экструзия": 0, "Итого": 0
        }

    for key in parsed:
        if key in user_stats[username]:
            user_stats[username][key] += parsed[key]

    user_days[username].add(now.date())

    total_pakov_all = sum(u['Паков'] for u in user_stats.values())
    total_ves_all = sum(u['Вес'] for u in user_stats.values())

    report = f"""
📦 Отчёт за смену:

🧮 Паков: {int(pakov)} шт
⚖️ Вес: {int(ves)} кг

♻️ Отходы:
🔧 Пакетосварка: {int(pak)} кг
🖨️ Флекса: {int(fle)} кг
🧵 Экструзия: {int(ext)} кг

🧾 Итого отходов: {int(total)} кг

📊 Всего продукции за период: {int(total_pakov_all)} паков / {int(total_ves_all)} кг
"""
    await update.message.reply_text(report.strip())

# /csv — файл с данными
async def cmd_csv(update, context):
    if not is_allowed(update):
        return
    file_path = get_csv_file()
    await update.message.reply_document(open(file_path, 'rb'))

# /stats — статистика
async def cmd_stats(update, context):
    if not is_allowed(update):
        return

    lines = ["📊 Статистика по пользователям:"]
    for user in user_stats:
        stats = user_stats[user]
        shifts = len(user_days.get(user, []))
        lines.append(
            f"👤 {user} ({shifts} смен):\n"
            f"  🧃 Паков: {int(stats['Паков'])} шт\n"
            f"  ⚖️  Вес: {int(stats['Вес'])} кг\n"
            f"  🛍️ Пакетосварка: {int(stats['Пакетосварка'])} кг\n"
            f"  🎨 Флекса: {int(stats['Флекса'])} кг\n"
            f"  🧵 Экструзия: {int(stats['Экструзия'])} кг\n"
            f"  ♻️ Итого отходов: {int(stats['Итого'])} кг"
        )

    await update.message.reply_text("\n".join(lines))

# /reset — сброс
async def cmd_reset(update, context):
    if not is_allowed(update):
        return
    user_stats.clear()
    user_days.clear()
    await update.message.reply_text("♻️ Статистика за месяц сброшена! (Excel не тронут)")

# /myid — Telegram ID
async def cmd_myid(update, context):
    if update.message.chat.type != "private":
        await update.message.reply_text("ℹ️ Запросите свой ID в личке бота.")
        return
    user_id = update.effective_user.id
    await update.message.reply_text(f"🆔 Ваш Telegram ID: `{user_id}`", parse_mode="Markdown")

# Запуск бота
def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN env variable is required")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("csv", cmd_csv))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
