import re
import os
import json
import csv
from collections import defaultdict

def extract_data(text):
    patterns = {
        'Паков': r'Паков\s*(\d+)',
        'Вес': r'Вес\s*(\d+)',
        'Пакетосварка': r'Пакетосварка\s*(\d+)',
        'Флексография': r'Флексография\s*(\d+)',
        'Экструзия': r'Экструзия\s*(\d+)',
        'Итого': r'Итого\s*(\d+)'
    }
    results = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            results[key] = int(match.group(1))
    return results

def format_report(parsed, stats):
    report = "📊 Отчет:"
"
    for k, v in parsed.items():
        report += f"{k}: {v}\n"
    report += "\n🏆 Статистика пользователей:
"
    for user, data in stats.items():
        report += f"{user}: {data}\n"
    return report

def append_to_csv(file, user, data):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        row = [user] + [data.get(k, 0) for k in ['Паков', 'Вес', 'Пакетосварка', 'Флексография', 'Экструзия', 'Итого']]
        writer.writerow(row)

def load_users(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(file, user, data):
    users = load_users(file)
    if user not in users:
        users[user] = defaultdict(int)
    for k, v in data.items():
        users[user][k] = users[user].get(k, 0) + v
    with open(file, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_stats(file):
    return load_users(file)

def reset_all_data():
    if os.path.exists("storage/data.csv"):
        os.remove("storage/data.csv")
    if os.path.exists("storage/users.json"):
        os.remove("storage/users.json")
