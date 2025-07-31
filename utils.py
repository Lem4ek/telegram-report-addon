import csv, os, json
from datetime import datetime

def extract_data(text):
    keys = ["Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого", "Брак"]
    results = {}
    for key in keys:
        for line in text.splitlines():
            if key in line:
                part = line.split()
                for item in part:
                    try:
                        results[key] = int(item)
                        break
                    except:
                        continue
    return results

def format_report(data):
    return "\n".join([f"{k}: {v}" for k, v in data.items()])

def append_to_csv(file, user, data):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    now = datetime.now()
    row = [now.strftime("%d.%m.%Y"), now.strftime("%H:%M"), user]
    for key in ["Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого", "Брак"]:
        row.append(data.get(key, ""))
    write_header = not os.path.exists(file) or os.stat(file).st_size == 0
    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Дата", "Время", "Пользователь", "Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого", "Брак"])
        writer.writerow(row)

def load_users(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(path, users):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, f)

def get_stats(users):
    lines = []
    for user, data in users.items():
        p = data.get("product", 0)
        w = data.get("waste", 0)
        ratio = round(p / w, 1) if w else "∞"
        lines.append(f"{user}: продукция={p}, брак={w}, соотношение={ratio}")
    return "\n".join(lines)