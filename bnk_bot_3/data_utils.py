import os
from openpyxl import Workbook, load_workbook
from datetime import datetime

DATA_DIR = "/config/bnk_bot/data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_file_path():
    return os.path.join(DATA_DIR, f"{datetime.now().strftime('%Y-%m')}.xlsx")

def save_entry(date, user, values, message_id):
    file_path = get_file_path()
    if os.path.exists(file_path):
        wb = load_workbook(file_path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append([
            "Дата", "Имя", "Паков", "Вес",
            "Пакетосварка", "Флекса", "Экструзия",
            "Итого", "Message ID"
        ])

    ws.append([
        date.strftime('%Y-%m-%d %H:%M'),
        user,
        values.get("Паков", 0),
        values.get("Вес", 0),
        values.get("Пакетосварка", 0),
        values.get("Флекса", 0),
        values.get("Экструзия", 0),
        values.get("Итого", 0),
        message_id
    ])
    wb.save(file_path)

def delete_entry_by_message_id(message_id):
    """Удаляет запись по ID сообщения"""
    file_path = get_file_path()
    if not os.path.exists(file_path):
        return
    wb = load_workbook(file_path)
    ws = wb.active
    for row in ws.iter_rows(min_row=2):
        if str(row[-1].value) == str(message_id):
            ws.delete_rows(row[0].row)
            wb.save(file_path)
            break

def get_csv_file():
    return get_file_path()

def generate_stats(stats):
    lines = ["📊 Статистика по пользователям:"]
    for user, data in stats.items():
        lines.append(
            f"{user}:\n"
            f"  🧃 Паков: {data['Паков']} шт\n"
            f"  🏋️‍♂️ Вес: {data['Вес']} кг\n"
            f"  ❌ Пакетосварка: {data['Пакетосварка']} кг\n"
            f"  🎨 Флекса: {data['Флекса']} кг\n"
            f"  🧵 Экструзия: {data['Экструзия']} кг\n"
            f"  📦 Итого отходов: {data['Итого']} кг"
        )
    return "\n".join(lines)
