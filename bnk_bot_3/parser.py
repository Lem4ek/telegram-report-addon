import re

def parse_message(text):
    result = {}
    lines = text.lower().splitlines()
    for line in lines:
        if "паков" in line:
            result["Паков"] = extract_number(line)
        elif "вес" in line:
            result["Вес"] = extract_number(line)
        elif "пакетосварка" in line:
            result["Пакетосварка"] = extract_number(line)
        elif "флекс" in line:
            result["Флекса"] = extract_number(line)
        elif "итого" in line:
            result["Итого"] = extract_number(line)
        elif "экструзия" in line:
            result["Экструзия"] = extract_number(line)
    return result

def extract_number(text):
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0