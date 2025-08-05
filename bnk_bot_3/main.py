from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from parser import parse_message
from data_utils import save_entry, generate_stats, get_csv_file
from datetime import datetime
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

user_stats = {}

async def handle_message(update, context):
    if not update.message or not update.message.text:
        return

    username = update.effective_user.first_name
    text = update.message.text
    values = parse_message(text)

    if values:
        for key in ["Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия"]:
            values.setdefault(key, 0)

        values["Итого"] = (
            values.get("Пакетосварка", 0)
            + values.get("Флекса", 0)
            + values.get("Экструзия", 0)
        )

        save_entry(datetime.now(), username, values)

        user_stats.setdefault(username, {
            'Паков': 0, 'Вес': 0,
            'Пакетосварка': 0, 'Флекса': 0,
            'Экструзия': 0, 'Итого': 0
        })
        for k in values:
            if k in user_stats[username] and isinstance(values[k], (int, float)):
                user_stats[username][k] += values[k]

        total_pakov_all = sum(u['Паков'] for u in user_stats.values())
        total_ves_all = sum(u['Вес'] for u in user_stats.values())

        report = (
            "📦 Отчёт за смену:"
            f"🧮 Паков: {values['Паков']} шт"
            f"⚖️ Вес: {values['Вес']} кг"
            "♻️ Отходы:"
            f"🔧 Пакетосварка: {values['Пакетосварка']} кг"
            f"🖨️ Флекса: {values['Флекса']} кг"
            f"🧵 Экструзия: {values['Экструзия']} кг"
            f"🧾 Итого отходов: {values['Итого']} кг"
            f"📊 Всего продукции за период: {total_pakov_all} паков / {total_ves_all} кг"
        )

        await update.message.reply_text(report)

async def cmd_csv(update, context):
    file_path = get_csv_file()
    await update.message.reply_document(open(file_path, 'rb'))

async def cmd_stats(update, context):
    await update.message.reply_text(generate_stats(user_stats))

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN env variable is required")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("csv", cmd_csv))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
