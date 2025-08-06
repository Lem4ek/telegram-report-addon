import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from parser import parse_message
from data_utils import save_entry, generate_stats, get_csv_file
from datetime import datetime, timedelta
from openpyxl import load_workbook
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

ALLOWED_USERS = [1198365511, 508532161]  # замени на свои ID
user_stats = {}
current_month = datetime.now().month
pending_updates = {}  # {message_id: {...}}

SAVE_DELAY = timedelta(minutes=2)  # тестовая задержка 2 минуты


def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def is_allowed(update):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    return username in ALLOWED_USERS or user_id in ALLOWED_USERS


def load_stats_from_excel():
    """Загружает статистику из текущего Excel в user_stats при старте"""
    file_path = get_csv_file()
    if not os.path.exists(file_path):
        return  # файла ещё нет — статистики нет

    wb = load_workbook(file_path)
    ws = wb.active

    for row in ws.iter_rows(min_row=2, values_only=True):  # пропускаем заголовок
        date, user, pakov, ves, paket, flexa, extru, itogo = row
        if not user:
            continue
        if user not in user_stats:
            user_stats[user] = {'Паков': 0.0, 'Вес': 0.0, 'Пакетосварка': 0.0,
                                'Флекса': 0.0, 'Экструзия': 0.0, 'Итого': 0.0}
        user_stats[user]['Паков'] += pakov or 0
        user_stats[user]['Вес'] += ves or 0
        user_stats[user]['Пакетосварка'] += paket or 0
        user_stats[user]['Флекса'] += flexa or 0
        user_stats[user]['Экструзия'] += extru or 0
        user_stats[user]['Итого'] += itogo or 0


async def delayed_save(message_id):
    """Ждёт SAVE_DELAY и сохраняет данные, если они ещё в буфере"""
    await asyncio.sleep(SAVE_DELAY.total_seconds())
    if message_id in pending_updates:
        data = pending_updates.pop(message_id)
        save_entry(data["time"], data["user"], data["values"])
        username = data["user"]
        values = data["values"]

        # Обновляем статистику
        user_stats.setdefault(username, {'Паков': 0.0, 'Вес': 0.0, 'Пакетосварка': 0.0,
                                         'Флекса': 0.0, 'Экструзия': 0.0, 'Итого': 0.0})
        for k in values:
            if k in user_stats[username] and isinstance(values[k], (int, float)):
                user_stats[username][k] += values[k]

        # Итоги по всем пользователям
        total_pakov_all = sum(u['Паков'] for u in user_stats.values())
        total_ves_all = sum(u['Вес'] for u in user_stats.values())

        # Формируем отчёт с двумя знаками после запятой
        report = f"""
📦 Отчёт за смену:

🧮 Паков: {values['Паков']:.2f} шт
⚖️ Вес: {values['Вес']:.2f} кг

♻️ Отходы:
🔧 Пакетосварка: {values['Пакетосварка']:.2f} кг
🖨️ Флекса: {values['Флекса']:.2f} кг
🧵 Экструзия: {values['Экструзия']:.2f} кг

🧾 Итого отходов: {values['Итого']:.2f} кг

📊 Всего продукции за период: {total_pakov_all:.2f} паков / {total_ves_all:.2f} кг
""".strip()

        await data["context"].bot.send_message(chat_id=data["chat_id"], text=report)


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
        values.setdefault(key, 0.0)

    values["Итого"] = safe_float(values.get("Пакетосварка", 0)) + safe_float(values.get("Флекса", 0)) + safe_float(values.get("Экструзия", 0))

    # Кладём данные в буфер без ответа в чат
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
        values.setdefault(key, 0.0)

    values["Итого"] = safe_float(values.get("Пакетосварка", 0)) + safe_float(values.get("Флекса", 0)) + safe_float(values.get("Экструзия", 0))

    pending_updates[message_id]["values"] = values
    pending_updates[message_id]["time"] = datetime.now()


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

    # Загружаем статистику из файла при старте
    load_stats_from_excel()

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
