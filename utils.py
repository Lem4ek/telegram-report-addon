
import csv
import os
from datetime import datetime

def extract_data(text):
    import re
    keys = {
        "Паков": r"Паков\s*-\s*(\d+)",
        "Вес": r"Вес\s*-\s*(\d+)",
        "Пакетосварка": r"Пакетосварка\s*-\s*(\d+)",
        "Флекса": r"(Флекса|Флексография)\s*-\s*(\d+)",
        "Экструзия": r"Экструзия\s*.*?(\d+)",
        "Итого": r"Итого\s+(\d+)"
    }
    results = {}
    for key, pattern in keys.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results[key] = int(match.group(1))
        else:
            results[key] = 0
    return results

def append_to_csv(file, user, data):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        row = [datetime.now().isoformat(), user] + [data[k] for k in ["Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого"]]
        writer.writerow(row)

def get_stats(file):
    import pandas as pd
    if not os.path.exists(file):
        return "Нет данных"
    df = pd.read_csv(file, header=None, names=["timestamp", "user", "Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого"])
    stats = df.groupby("user")[["Паков", "Итого"]].sum()
    return stats.to_string()

def export_csv(update, context, file):
    if os.path.exists(file):
        with open(file, "rb") as f:
            return context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename="data.csv")
    else:
        return context.bot.send_message(chat_id=update.effective_chat.id, text="Файл не найден")

def reset_all_data(file):
    if os.path.exists(file):
        os.remove(file)
