import os
from openpyxl import Workbook, load_workbook
from datetime import datetime

# Папка для хранения Excel-файлов
DATA_DIR = "/config/bnk_bot/data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_file_path():
    """Возвращает путь к текущему Excel-файлу за месяц."""
    return os.path.join(DATA_DIR, f"{datetime.now().strftime('%Y-%m')}.xlsx")

def save_entry(date, user, values, message_id=None):
    """
    Сохраняет данные в Excel.
    message_id оставлен на будущее — сейчас не используется.
    """
    file_path = get_file_path()

    if os.path.exists(file_path):
        wb = load_workbook(file_path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append([
            "Дата", "Имя", "Паков", "Вес",
            "Пакетосварка", "Флекса", "Экструзия", "Итого"
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
    ])
    wb.save(file_path)

def get_csv_file():
    """Возвращает путь к текущему Excel-файлу."""
    return get_file_path()

def generate_stats(stats):
    """Генерирует текстовую статистику по пользователям (с десятичными значениями)."""
    lines = ["📊 Статистика по пользователям:"]
    for user, data in stats.items():
        lines.append(
            f"{user}:\n"
            f"  📦 Паков: {data['Паков']:.2f} шт\n"
            f"  ⚖️ Вес: {data['Вес']:.2f} кг\n"
            f"  🛍️ Пакетосварка: {data['Пакетосварка']:.2f} кг\n"
            f"  🧵 Экструзия: {data['Экструзия']:.2f} кг\n"
            f"  🎨 Флекса: {data['Флекса']:.2f} кг\n"
            f"  ♻️ Итого отходов: {data['Итого']:.2f} кг"
        )
    return "\n".join(lines)
