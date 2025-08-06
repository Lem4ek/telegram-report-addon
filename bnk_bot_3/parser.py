import re

def parse_message(text):
    result = {}

    # Приводим текст к нижнему регистру и убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text.strip().lower())

    # Паков (оставляем как целое)
    match = re.search(r'паков\s*[-–:]?\s*(\d+(?:[.,]\d+)?)', text)
    if match:
        result["Паков"] = float(match.group(1).replace(',', '.'))

    # Вес
    match = re.search(r'вес\s*[-–:]?\s*(\d+(?:[.,]\d+)?)', text)
    if match:
        result["Вес"] = float(match.group(1).replace(',', '.'))

    # Пакетосварка
    match = re.search(r'пакетосварка\s*[-–:]?\s*(\d+(?:[.,]\d+)?)', text)
    if match:
        result["Пакетосварка"] = float(match.group(1).replace(',', '.'))

    # Флекса или Флексография
    match = re.search(r'флекс(?:ография)?\s*[-–:]?\s*(\d+(?:[.,]\d+)?)', text)
    if match:
        result["Флекса"] = float(match.group(1).replace(',', '.'))

    # Экструзия с мягкими (м) и твёрдыми (т) отходами
    match = re.search(
        r'экструзия\s*(?:м\s*(\d+(?:[.,]\d+)?))?\s*(?:т\s*(\d+(?:[.,]\d+)?))?',
        text
    )
    if match:
        m_value = float(match.group(1).replace(',', '.')) if match.group(1) else 0
        t_value = float(match.group(2).replace(',', '.')) if match.group(2) else 0
        result["Экструзия"] = m_value + t_value

    # Итого
    match = re.search(r'итого\s*[-–:]?\s*(\d+(?:[.,]\d+)?)', text)
    if match:
        result["Итого"] = float(match.group(1).replace(',', '.'))

    return result
