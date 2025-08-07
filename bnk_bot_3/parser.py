import re

def parse_message(text):
    text = text.lower().strip()

    results = {
        "Паков": 0,
        "Вес": 0,
        "Пакетосварка": 0,
        "Флекса": 0,
        "Экструзия": 0,
    }

    # Шаблоны
    patterns = {
        "Паков": r"(паков|паки|упаковка)\s*[:\-]?\s*(\d+(?:[.,]\d+)?)",
        "Вес": r"вес\s*[:\-]?\s*(\d+(?:[.,]\d+)?)",
        "Пакетосварка": r"пакетосварка\s*[:\-]?\s*(\d+(?:[.,]\d+)?)",
        "Флекса": r"флекс[а-я]*\s*[:\-]?\s*(\d+(?:[.,]\d+)?)",
        "Экструзия": r"(экструзия|экструдер)[^\d]*(м)?\s*([\d.,]+)?\s*(т)?[^\d]*([\d.,]+)?"
    }

    # Обработка экструзии
    match = re.search(patterns["Экструзия"], text)
    if match:
        m_val = match.group(3)
        t_val = match.group(5)
        m = float(m_val.replace(",", ".")) if m_val else 0
        t = float(t_val.replace(",", ".")) if t_val else 0
        results["Экструзия"] = round(m + t, 2)

    # Остальные ключи
    for key in ["Паков", "Вес", "Пакетосварка", "Флекса"]:
        match = re.search(patterns[key], text)
        if match:
            value = match.group(2) if len(match.groups()) > 1 else match.group(1)
            try:
                results[key] = round(float(value.replace(",", ".")), 2)
            except ValueError:
                pass

    # Если нет слова "вес" или "всего", считаем, что это не отчет
    if not re.search(r"\b(вес|всего)\b", text):
        return {}

    return results
