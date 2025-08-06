from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from parser import parse_message
from data_utils import save_entry, generate_stats, get_csv_file
from datetime import datetime, timedelta
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

# Список разрешённых пользователей (по ID или имени)
ALLOWED_USERS = [1198365511, 508532161]  # замени на свои ID

user_stats = {}
current_month = datetime.now().month  # для авто-сброса
pending_updates = {}  # {message_id: {"user": str, "values": dict, "time": datetime, "chat_id": int}}

SAVE_DELAY = timedelta(minutes=2)  # 2 минуты для теста

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def is_allowed(update):
    username = update.effective_user.first_name
    user_id = update.effective_user.id
    return username in ALLOWED_USERS or user_id in ALLOWED_USERS

async def process_save_jobs(context):
    """Проверяем буфер и сохраняем данные, которые ждут более SAVE_DELAY"""
    now = datetime.now()
    to_save = [mid for mid, data in pending_updates.items() if now - data["time"] >= SAVE_DELAY]
    for mid in to_save:
        data = pending_updates.pop(mid)
        save_entry(data["time"], data["user"], data["values"])
        # Обновляем статистику
        username = data["user"]
        values = data["values"]
        user_stats.setdefault(username, {'Паков': 0, 'Вес': 0, 'Пакетосварка': 0,
                                         'Флекса': 0, 'Экструзия': 0, 'Итого': 0})
        for k in values:
            if k in user_stats[username] and isinstance(values[k], (int, float)):
                user_stats[username][k] += values[k]
        # Сообщение в чат о сохранении
        await context.bot.send_message(chat_id=data["chat_id"], text="✅ Данные сохранены")

async def handle_message(update, context):
    global current_month

    # Авто-сброс в начале месяца
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

    # Проверка: найдено ли 3 и более ключа
    found_keys_count = sum(1 for v in values.values() if v not in (0, "", None))
    if found_keys_count < 3:
        return

    # Заполняем отсутствующие ключи нулями
    for key in ["Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия"]:
        values.setdefault(key, 0)

    pak = safe_int(values.get("Пакетосварка", 0))
    fle = safe_int(values.get("Флекса", 0))
    ext = safe_int(values.get("Экструзия", 0))
    values["Итого"] = pak + fle + ext

    # Кладём в буфер
    pending_updates[update.message.message_id] = {
        "user": username,
        "values": values,
        "time": datetime.now(),
        "chat_id": update.message.chat_id
    }

    await update.message.reply_text(
        "⏳ Данные приняты. В течение 2 минут можно отредактировать или удалить сообщение."
    )

async def handle_edited_message(update, context):
    """Обновление данных при редактировании сообщения"""
    if not update.edited_message or not update.edited_message.text:
        return

    message_id = update.edited_message.message_id
    if message_id not in pending_updates:
        return  # сообщение уже сохранено или не отслеживается

    text = update.edited_message.text
    values = parse_message(text)

    found_keys_count = sum(1 for v in values.values() if v not in (0, "", None))
    if found_keys_count < 3:
        return

    for key in ["Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия"]:
        values.setdefault(key, 0)

    pak = safe_int(values.get("Пакетосварка", 0))
    fle = safe_int(values.get("Флекса", 0))
    ext = safe_int(values.get("Экструзия", 0))
    values["Итого"] = pak + fle + ext

    pending_updates[message_id]["values"] = values
    pending_updates[message_id]["time"] = datetime.now()

    await update.edited_message.reply_text("✏️ Данные обновлены.")

async def handle_deleted_message(update, context):
    """Удаление записи из буфера при удалении сообщения"""
    if not update.message:
        return
    message_id = update.message.message_id
    if message_id in pending_updates:
        pending_updates.pop(message_id)

async def cmd_csv(update, context):
    if not is_allowed(update):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    file_path = get_csv_file()
    await update.message.reply_document(open(file_path, 'rb'))

async def cmd_stats(update, context):
    if not is_allowed(update):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    await update.message.reply_text(generate_stats(user_stats))

async def cmd_reset(update, context):
    if not is_allowed(update):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    user_stats.clear()
    pending_updates.clear()
    await update.message.reply_text("♻️ Статистика и буфер сброшены! (Excel не тронут)")

async def cmd_myid(update, context):
    if update.message.chat.type != "private":
        await update.message.reply_text("ℹ️ Запросите свой ID в личном чате с ботом.")
        return
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"🆔 Ваш Telegram ID: `{user_id}`",
        parse_mode="Markdown"
    )

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN env variable is required")

    app = ApplicationBuilder().token(TOKEN).build()
    app.job_queue.run_repeating(process_save_jobs, interval=60, first=60)

    app.add_handler(CommandHandler("csv", cmd_csv))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_edited_message))
    # Удалённые сообщения — работает только в определённых режимах Telegram API
    # app.add_handler(MessageHandler(filters.DELETED, handle_deleted_message))

    app.run_polling()

if __name__ == "__main__":
    main()
