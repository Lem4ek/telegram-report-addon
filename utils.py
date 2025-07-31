import re, csv, os, json
from datetime import datetime

PATTERNS = {
    "паков": r"Паков\s*[-:–—]?\s*(\d+)",
    "вес": r"Вес\s*[-:–—]?\s*(\d+)",
    "пакетосварка": r"Пакетосварка\s*[-:–—]?\s*(\d+)",
    "флекса": r"(Флекса|Флексография)\s*[-:–—]?\s*(\d+)",
    "экструзия": r"Экструзия[^\d]*(\d+)?[^\d]*(\d+)?",
    "итого": r"Итого\s*[-:–—]?\s*(\d+)"
}

def extract_data(text):
    results = {}
    for key, pattern in PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if key == "экструзия":
                results[key] = sum(int(g) for g in match.groups() if g)
            else:
                results[key] = int(match.group(1))
    return results

def format_report(parsed):
    lines = ["📦 Отчёт за смену:\n"]
    if "паков" in parsed: lines.append(f"🧮 Паков: {parsed['паков']} шт")
    if "вес" in parsed: lines.append(f"⚖️ Вес: {parsed['вес']} кг")
    lines.append("\n♻️ Отходы:")
    if "пакетосварка" in parsed: lines.append(f"🔧 Пакетосварка: {parsed['пакетосварка']} кг")
    if "флекса" in parsed: lines.append(f"🖨️ Флекса: {parsed['флекса']} кг")
    if "экструзия" in parsed: lines.append(f"🧵 Экструзия: {parsed['экструзия']} кг")
    if "итого" in parsed: lines.append(f"\n🧾 Итого отходов: {parsed['итого']} кг")
    return "\n".join(lines)

def append_to_csv(file, user, parsed):
    exists = os.path.exists(file)
    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["Дата", "Пользователь", "Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого"])
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            user,
            parsed.get("паков", ""),
            parsed.get("вес", ""),
            parsed.get("пакетосварка", ""),
            parsed.get("флекса", ""),
            parsed.get("экструзия", ""),
            parsed.get("итого", "")
        ]
        writer.writerow(row)

def load_users(path):
    return json.load(open(path)) if os.path.exists(path) else {}

def save_users(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_stats(file):
    if not os.path.exists(file):
        return "Нет данных."
    with open(file, encoding="utf-8") as f:
        lines = f.readlines()[1:]
    return f"👥 Всего записей: {len(lines)}"