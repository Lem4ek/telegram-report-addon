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
            result["Экструзия"] = extract_extrusion_numbers(line)
    return result

def extract_number(text):
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0

def extract_extrusion_numbers(text):
    """Парсит мягкие и твёрдые отходы из строки 'мXX тYY' и возвращает сумму."""
    m_val = 0
    t_val = 0

    m_match = re.search(r"м(\d+)", text)
    if m_match:
        m_val = int(m_match.group(1))

    t_match = re.search(r"т(\d+)", text)
    if t_match:
        t_val = int(t_match.group(1))

    return m_val + t_val
