import re

def normalize_number(value):
    try:
        return float(value.replace(",", "."))
    except:
        return 0

def parse_extrusion(text):
    m = re.search(r"[мm]\s*-?\s*(\d+[.,]?\d*)", text, re.IGNORECASE)
    t = re.search(r"[тt]-?\s*(\d+[.,]?\d*)", text, re.IGNORECASE)
    return {
        "Экструзия_м": normalize_number(m.group(1)) if m else 0,
        "Экструзия_т": normalize_number(t.group(1)) if t else 0
    }

def parse_message(text):
    text = text.lower()

    # Ключевые слова и их синонимы
    synonyms = {
        "паков": ["паков", "паки", "упаковок"],
        "вес": ["вес", "кг", "килограмм"],
        "пакетосварка": ["пакетосварка", "пакет", "сварка"],
        "флекса": ["флекса", "флексография", "флексо"],
        "экструзия": ["экструзия", "экструдер"]
    }

    results = {}

    # Паков
    match = re.search(r"(паков|паки|упаковок)[^\d]*(\d+)", text)
    if match:
        results["Паков"] = int(match.group(2))

    # Вес
    match = re.search(r"(вес|кг|килограмм)[^\d]*(\d+[.,]?\d*)", text)
    if match:
        results["Вес"] = normalize_number(match.group(2))

    # Пакетосварка
    match = re.search(r"(пакетосварка|пакет|сварка)[^\d]*(\d+[.,]?\d*)", text)
    if match:
        results["Пакетосварка"] = normalize_number(match.group(2))

    # Флекса
    match = re.search(r"(флекса|флексография|флексо)[^\d]*(\d+[.,]?\d*)", text)
    if match:
        results["Флекса"] = normalize_number(match.group(2))

    # Экструзия (м и т отдельно)
    if any(word in text for word in synonyms["экструзия"]):
        ext = parse_extrusion(text)
        results["Экструзия"] = round(ext["Экструзия_м"] + ext["Экструзия_т"], 2)

    return results
