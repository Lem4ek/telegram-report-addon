# /app/data_utils.py
import os
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from datetime import datetime
import calendar

def get_excel_path(folder: str) -> str:
    os.makedirs(folder, exist_ok=True)
    filename = f"{datetime.now().strftime('%Y-%m')}.xlsx"
    return os.path.join(folder, filename)

def save_data(data: dict, user: str, user_id: int, folder: str):
    path = get_excel_path(folder)
    file_exists = os.path.isfile(path)

    if file_exists:
        wb = load_workbook(path)
    else:
        wb = Workbook()

    sheet = wb.active
    sheet.title = "Данные"

    if not file_exists:
        headers = ["Дата", "Пользователь", "ID", "Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого"]
        sheet.append(headers)

    sheet.append([
        datetime.now().strftime('%d.%m.%Y'),
        user,
        user_id,
        data.get("Паков", 0),
        data.get("Вес", 0),
        data.get("Пакетосварка", 0),
        data.get("Флекса", 0),
        data.get("Экструзия", ""),
        data.get("Итого", 0),
    ])

    wb.save(path)

def export_excel(folder: str) -> str:
    path = get_excel_path(folder)
    return path if os.path.isfile(path) else None

def reset_month_data(folder: str):
    path = get_excel_path(folder)
    if os.path.exists(path):
        os.remove(path)

def get_user_stats(folder: str) -> str:
    path = get_excel_path(folder)
    if not os.path.exists(path):
        return "Нет данных."

    wb = load_workbook(path)
    sheet = wb.active
    stats = {}

    for row in sheet.iter_rows(min_row=2, values_only=True):
        name = row[1]
        pakov = row[3] or 0
        ves = row[4] or 0
        otxody = (row[5] or 0) + (row[6] or 0)
        if name not in stats:
            stats[name] = {"продукция": 0, "отходы": 0}
        stats[name]["продукция"] += ves
        stats[name]["отходы"] += otxody

    msg = "📊 Статистика по пользователям:\n"
    for user, d in stats.items():
        msg += f"👤 {user} — Продукция: {d['продукция']} кг, Отходы: {d['отходы']} кг\n"
    return msg
