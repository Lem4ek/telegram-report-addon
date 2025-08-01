# /app/parser.py
import re

def extract_number(line):
    match = re.search(r"(\d+)", line.replace(" ", ""))
    return int(match.group(1)) if match else 0

def extract_report_data(text: str) -> dict:
    lines = text.lower().splitlines()
    data = {
        "Паков": 0,
        "Вес": 0,
        "Пакетосварка": 0,
        "Флекса": 0,
        "Экструзия": "",
        "Итого": 0,
    }

    for line in lines:
        if "паков" in line:
            data["Паков"] = extract_number(line)
        elif "вес" in line:
            data["Вес"] = extract_number(line)
        elif "пакетосварк" in line:
            data["Пакетосварка"] = extract_number(line)
        elif "флексо" in line or "флекса" in line:
            data["Флекса"] = extract_number(line)
        elif "экструзия" in line:
            data["Экструзия"] = line.strip()
        elif "итого" in line:
            data["Итого"] = extract_number(line)

    if any([data["Паков"], data["Вес"], data["Пакетосварка"], data["Флекса"], data["Итого"]]):
        return data
    return None
