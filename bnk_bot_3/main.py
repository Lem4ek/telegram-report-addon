import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from parser import parse_message
from data_utils import save_entry, generate_stats, get_csv_file
from datetime import datetime, timedelta
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

ALLOWED_USERS = [1198365511, 508532161]  # замени на свои ID
user_stats = {}
current_month = datetime.now().month
pending_updates = {}  # {message_id: {...}}

SAVE_DELAY = timedelta(minutes=2)  # тестовая задержка 2 минуты

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def is_allowed(update):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    return username in ALLOWED_USERS or user_id in ALLOWED_USERS

async def delayed_save(message_id):
    """Ожидает SAVE_DELAY и сохраняет данные, если они ещё в буфере"""
    await asyncio.sleep(SAVE_DELAY.total_seconds())
    if message_id in pending_updates:
        data = pending_updates.pop(message_id)
        save_entry(data["time"], data["user"], data["values"])
        username = data["user"]
        values = data["values"]

        user_stats.setdefault(username, {'Паков': 0, 'Вес': 0, 'Пакетосварка': 0,
                                         'Флекса': 0, 'Экструзия': 0, 'Итого': 0})
        for k in values:
            if k in user_stats[username] and isinstance(values[k], (int, float)):
                user_stats[username][k] += values[k]

        await data["context"].bot.send_message(chat_id=data["chat_id"], text="✅ Данные сохранены")

async def handle_message(update, context):
    global current_month
    month_now = datetime.now().month
    if month_now != current_month:
        user_stats.clear()
        pending_updates.clear()
        current_month = month_now

    if not update.message or not update.message.text:
        return

    username = update.effective_user.first_name
    text = update.message.text
    values = parse_message(text)
    if not values:
        return

    if sum(1 for v in values.values() if v not in (0, "", None)) < 3:
        return

    for key in ["Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия"]:
        values.setdefault(key, 0)

    pak = safe_int(values.get("Пакетосварка", 0))
    fle = safe_int(values.get("Флекса", 0))
    ext = safe_int(values.get("Экструзия", 0))
    values["Итого"] = pak + fle + ext

    # Предварительный общий итог
    total_pakov_all = sum(u['Паков'] for u in user_stats.values()) + values['Паков']
    total_ves_all = sum(u['Вес'] for u in user_stats.values()) + values['Вес']

    # Формируем красивый отчёт
    report = f"""
📦 Отчёт за смену:

🧮 Паков: {values['Паков']} шт
⚖️ Вес: {values['Вес']} кг

♻️ Отходы:
🔧 Пакетосварка: {pak} кг
🖨️ Флекса: {fle} кг
🧵 Экструзия: {ext} кг

🧾 Итого отходов: {values['Итого']} кг

📊 Всего продукции за период: {total_pakov_all} паков / {total_ves_all} кг
""".strip()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=report)

    # Кладём данные в буфер
    message_id = update.message.message_id
    pending_updates[message_id] = {
        "user": username,
        "values": values,
        "time": datetime.now(),
        "chat_id": update.effective_chat.id,
        "context": context
    }

    asyncio.create_task(delayed_save(message_id))

async def handle_edited_message(update, context):
    if not update.edited_message or not update.edited_message.text:
        return
    message_id = update.edited_message.message_id
    if message_id not in pending_updates:
        return

    text = update.edited_message.text
    values = parse_message(text)
    if sum(1 for v in values.values() if v not in (0, "", None)) < 3:
        return

    for key in ["Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия"]:
        values.setdefault(key, 0)

    pak = safe_int(values.get("Пакетосварка", 0))
    fle = safe_int(values.get("Флекса", 0))
    ext = safe_int(values.get("Экструзия", 0))
    values["Итого"] = pak + fle + ext

    pending_updates[message_id]["values"] = values
    pending_updates[message_id]["time"] = datetime.now()

    await context.bot.send_message(chat_id=update.effective_chat.id, text="✏️ Данные обновлены.")

async def cmd_csv(update, context):
    if not is_allowed(update):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⛔ Нет доступа.")
        return
    file_path = get_csv_file()
    await context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_path, 'rb'))

async def cmd_stats(update, context):
    if not is_allowed(update):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⛔ Нет доступа.")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=generate_stats(user_stats))

async def cmd_reset(update, context):
    if not is_allowed(update):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⛔ Нет доступа.")
        return
    user_stats.clear()
    pending_updates.clear()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="♻️ Статистика и буфер сброшены! (Excel не тронут)")

async def cmd_myid(update, context):
    if update.message.chat.type != "private":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="ℹ️ Запросите ID в личке.")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"🆔 Ваш Telegram ID: `{update.effective_user.id}`",
                                   parse_mode="Markdown")

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN env variable is required")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("csv", cmd_csv))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_edited_message))

    app.run_polling()

if __name__ == "__main__":
    main()
