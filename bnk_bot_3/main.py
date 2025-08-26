import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from parser import parse_message
from data_utils import save_entry, generate_stats, get_csv_file
from datetime import datetime, timedelta
from openpyxl import load_workbook
import os
import matplotlib.pyplot as plt
import pandas as pd

TOKEN = os.getenv("TELEGRAM_TOKEN")

ALLOWED_USERS = [1198365511, 508532161]  # замени на свои ID
user_stats = {}
current_month = datetime.now().month
pending_updates = {}

SAVE_DELAY = timedelta(minutes=2)  # задержка перед записью/отправкой


def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def is_allowed(update):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    return username in ALLOWED_USERS or user_id in ALLOWED_USERS


# ✅ Фильтр отчёта: требуем присутствие всех ключевых разделов с вариантами слов
def is_valid_report(text: str) -> bool:
    t = text.lower()
    groups = [
        ["паков", "паки", "упаков"],  # Паков/Паки/Упаков...
        ["вес"],                      # Вес
        ["отход"],                    # Отход/Отходы
        ["пакетосвар"],               # Пакетосварка
        ["экструз", "экструд"],       # Экструзия/Экструдер
    ]
    return all(any(v in t for v in grp) for grp in groups)


def load_stats_from_excel():
    """Загружает статистику из текущего Excel в user_stats при старте"""
    file_path = get_csv_file()
    if not os.path.exists(file_path):
        return

    wb = load_workbook(file_path)
    ws = wb.active

    for row in ws.iter_rows(min_row=2, values_only=True):
        date, user, pakov, ves, paket, flexa, extru, itogo = row
        if not user:
            continue
        if user not in user_stats:
            user_stats[user] = {'Паков': 0.0, 'Вес': 0.0, 'Пакетосварка': 0.0,
                                'Флекса': 0.0, 'Экструзия': 0.0, 'Итого': 0.0, 'Смен': 0}
            user_stats[user]['Смен'] += 1
        user_stats[user]['Паков'] += safe_float(pakov)
        user_stats[user]['Вес'] += safe_float(ves)
        user_stats[user]['Пакетосварка'] += safe_float(paket)
        user_stats[user]['Флекса'] += safe_float(flexa)
        user_stats[user]['Экструзия'] += safe_float(extru)
        user_stats[user]['Итого'] += safe_float(itogo)


async def delayed_save(message_id):
    try:
        await asyncio.sleep(SAVE_DELAY.total_seconds())
        if message_id not in pending_updates:
            return

        data = pending_updates.pop(message_id)
        bot = data["context"].bot
        chat_id = data["chat_id"]
        username = data["user"]
        values = data["values"]

        # 1) Сохраняем в файл
        save_entry(data["time"], username, values)

        # 2) Обновляем статистику в памяти
        user_stats.setdefault(username, {
            'Паков': 0.0, 'Вес': 0.0, 'Пакетосварка': 0.0,
            'Флекса': 0.0, 'Экструзия': 0.0, 'Итого': 0.0, 'Смен': 0
        })
        for k, v in values.items():
            if k in user_stats[username] and isinstance(v, (int, float)):
                user_stats[username][k] += v
        user_stats[username]['Смен'] += 1

        total_pakov_all = sum(u.get('Паков', 0.0) for u in user_stats.values())
        total_ves_all = sum(u.get('Вес', 0.0) for u in user_stats.values())

        # 3) Формируем отчёт
        report = f"""
📦 Отчёт за смену:

📦  Паков: {values.get('Паков', 0.0):.2f} шт
⚖️ Вес: {values.get('Вес', 0.0):.2f} кг

♻️ Отходы:
🛍️ Пакетосварка: {values.get('Пакетосварка', 0.0):.2f} кг
🎨 Флекса: {values.get('Флекса', 0.0):.2f} кг
🧵 Экструзия: {values.get('Экструзия', 0.0):.2f} кг

🧾 Итого отходов: {values.get('Итого', 0.0):.2f} кг

📊 Всего продукции за период: {total_pakov_all:.2f} паков / {total_ves_all:.2f} кг
""".strip()

        # 4) Отправляем отчёт в чат
        await bot.send_message(chat_id=chat_id, text=report)

    except Exception as e:
        # Лог и короткое уведомление вместо молчаливого падения
        import traceback
        print("delayed_save error:", e)
        print(traceback.format_exc())
        try:
            await data["context"].bot.send_message(
                chat_id=data.get("chat_id"),
                text="✅ Отчёт сохранён, но не удалось отправить форматированное сообщение. "
                     f"(ошибка: {e})"
            )
        except Exception:
            pass


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

    # ✅ Фильтр отчёта
    if not is_valid_report(text):
        return

    values = parse_message(text)
    if not values:
        return

    # Минимум 3 непустых поля
    if sum(1 for v in values.values() if v not in (0, "", None)) < 3:
        return

    for key in ["Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия"]:
        values.setdefault(key, 0.0)

    values["Итого"] = safe_float(values.get("Пакетосварка", 0)) + safe_float(values.get("Флекса", 0)) + safe_float(values.get("Экструзия", 0))

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

    if not is_valid_report(text):
        return

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


async def cmd_graf(update, context):
    if not is_allowed(update):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⛔ Нет доступа.")
        return

    file_path = get_csv_file()
    if not os.path.exists(file_path):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Файл данных не найден.")
        return

    # читаем .xlsx с текущими колонками
    df = pd.read_excel(file_path)
    if df.empty:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ В файле нет данных.")
        return

    # нормализуем названия столбцов на всякий случай
    df.columns = ["Дата", "Имя", "Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого"]
    # дата как datetime
    try:
        df["Дата"] = pd.to_datetime(df["Дата"])
    except Exception:
        pass

    # =============== ГРАФИК 1: Производство и отходы по дням ===============
    daily = (df.groupby(df["Дата"].dt.date)[["Вес", "Итого"]]
               .sum()
               .reset_index()
               .rename(columns={"Дата": "День"}))

    x = list(range(len(daily)))
    width = 0.4
    fig, ax = plt.subplots()

    bars_weight = ax.bar([i - width/2 for i in x], daily["Вес"], width=width, label="Вес")
    bars_waste  = ax.bar([i + width/2 for i in x], daily["Итого"], width=width, label="Итого отходов")

    ax.set_title("Производство и отходы по дням")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Кг")
    ax.set_xticks(x, [str(d) for d in daily["День"]], rotation=45, ha="right")
    ax.legend()

    # ——— Умные подписи: не каждую, а с шагом (зависит от числа столбиков)
    def smart_step(n: int) -> int:
        if n <= 12:   return 1
        if n <= 20:   return 2
        if n <= 35:   return 3
        return max(1, n // 12)

    step = smart_step(len(x))

    def add_labels(bars, fmt="{:.0f}", dy=3, every=1):
        for i, b in enumerate(bars):
            # показываем каждую every-ю, а также всегда первую и последнюю
            if i % every != 0 and i not in (0, len(bars) - 1):
                continue
            v = b.get_height()
            ax.annotate(fmt.format(v),
                        xy=(b.get_x() + b.get_width()/2, v),
                        xytext=(0, dy), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8)

    # Немного «развести» подписи двух серий по высоте
    add_labels(bars_weight, fmt="{:.0f}", dy=8,  every=step)
    add_labels(bars_waste,  fmt="{:.0f}", dy=3,  every=step)

    # Дать запас сверху, чтобы подписи не упирались в верх графика
    ax.margins(y=0.15)

    fig.tight_layout()
    img1 = "/tmp/graf1_daily.png"
    fig.savefig(img1)
    plt.close(fig)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img1, "rb"))


    # =============== ГРАФИК 2: ТОП производители по весу (кг) ===============
    top_users = (df.groupby("Имя")["Вес"]
                   .sum()
                   .sort_values(ascending=False)
                   .head(10))
    plt.figure()
    plt.bar(top_users.index, top_users.values)
    plt.title("ТОП производители по весу (кг)")
    plt.xlabel("Пользователь")
    plt.ylabel("Кг")
    plt.xticks(rotation=45, ha="right")

    # подписи кг
    for i, v in enumerate(top_users.values):
        plt.text(i, v, f"{v:.0f}", ha="center", va="bottom")

    plt.tight_layout()
    img2 = "/tmp/graf2_top_weight.png"
    plt.savefig(img2)
    plt.close()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img2, "rb"))

    # =============== ГРАФИК 3: Доля отходов в общей массе (pie) ===============
    total_weight = float(df["Вес"].sum())
    total_waste = float(df["Итого"].sum())
    good = max(total_weight - total_waste, 0)

    plt.figure()
    plt.pie([good, total_waste],
            labels=["Продукция", "Отходы"],
            autopct="%1.1f%%",
            startangle=90)
    plt.axis("equal")
    plt.title("Доля отходов в общей массе")
    img3 = "/tmp/graf3_share.png"
    plt.savefig(img3)
    plt.close()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img3, "rb"))

    # =============== ГРАФИК 4: ТОП по браку (кг) ===============
    agg = (df.groupby("Имя")[["Итого"]]
             .sum()
             .reset_index())
    top_kg = agg.sort_values("Итого", ascending=False).head(10)

    plt.figure()
    plt.bar(top_kg["Имя"], top_kg["Итого"])
    plt.title("Топ по браку (кг)")
    plt.xlabel("Пользователь")
    plt.ylabel("Брак, кг")
    plt.xticks(rotation=45, ha="right")

    # подписи кг над столбцами
    for i, v in enumerate(top_kg["Итого"]):
        plt.text(i, v, f"{v:.0f}", ha="center", va="bottom")

    plt.tight_layout()
    img4 = "/tmp/graf4_defect_kg.png"
    plt.savefig(img4)
    plt.close()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img4, "rb"))




async def cmd_import(update, context):
    if not is_allowed(update):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⛔ Нет доступа.")
        return
    # Удалим текущий Excel-файл и сбросим статистику
    from pathlib import Path
    current_file = Path(get_csv_file())
    if current_file.exists():
        current_file.unlink()
        user_stats.clear()

    if not update.message.document:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="📄 Пожалуйста, отправьте Excel-файл.")
        return

    file = await update.message.document.get_file()
    file_path = f"/tmp/imported.xlsx"
    await file.download_to_drive(file_path)

    try:
        wb = load_workbook(file_path)
        ws = wb.active
        imported = 0

        from data_utils import save_entry

        for row in ws.iter_rows(min_row=2, values_only=True):
            date_str, user, pakov, ves, paket, flexa, extru, itogo = row
            if not user:
                continue

            try:
                if isinstance(date_str, str):
                    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                else:
                    date = date_str
            except Exception:
                date = datetime.now()

            values = {
                "Паков": pakov or 0,
                "Вес": ves or 0,
                "Пакетосварка": paket or 0,
                "Флекса": flexa or 0,
                "Экструзия": extru or 0,
                "Итого": itogo or 0
            }

            save_entry(date, user, values)

            if user not in user_stats:
                user_stats[user] = {
                    'Паков': 0.0, 'Вес': 0.0, 'Пакетосварка': 0.0,
                    'Флекса': 0.0, 'Экструзия': 0.0, 'Итого': 0.0, 'Смен': 0
                }

            user_stats[user]['Паков'] += values["Паков"]
            user_stats[user]['Вес'] += values["Вес"]
            user_stats[user]['Пакетосварка'] += values["Пакетосварка"]
            user_stats[user]['Флекса'] += values["Флекса"]
            user_stats[user]['Экструзия'] += values["Экструзия"]
            user_stats[user]['Итого'] += values["Итого"]
            user_stats[user]['Смен'] += 1

            imported += 1

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"✅ Импорт завершён. Загружено и сохранено записей: {imported}")

    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"❌ Ошибка при импорте: {e}")


def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN env variable is required")

    load_stats_from_excel()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("csv", cmd_csv))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(CommandHandler("graf", cmd_graf))
    app.add_handler(MessageHandler(filters.Document.ALL & filters.Caption("/import"), cmd_import))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_edited_message))

    app.run_polling()


if __name__ == "__main__":
    main()
