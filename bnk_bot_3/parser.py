import re

# Числа вида: 1 500, 1392,2, 16.4, 0.9, 12 и т.п.
NUM_RE = re.compile(r'(?:(?:\d{1,3}(?:[ \u00A0]\d{3})+|\d+)(?:[.,]\d+)?)')

def _to_float(s: str) -> float:
    s = str(s).replace('\u00A0', '').replace(' ', '').replace(',', '.')
    try:
        return float(s)
    except Exception:
        return 0.0

def _sum_numbers_in_line(line: str) -> float:
    return sum(_to_float(m.group(0)) for m in NUM_RE.finditer(line))

def _extract_number(text: str, patterns: str) -> float:
    """
    Ищет первое число в той же строке, где встречается один из шаблонов (patterns).
    Полезно для 'Паков', 'Вес' и т.п.
    """
    # Берём по строкам, чтобы не тянуть числа из соседних строк
    pat = re.compile(rf'(?:{patterns})', re.IGNORECASE)
    best = 0.0
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if pat.search(line):
            # число в этой же строке (первое после двоеточия/дефиса/пробелов — не строго)
            m = re.search(r'([0-9]{1,3}(?:[ \u00A0]\d{3})+|\d+)(?:[.,]\d+)?', line)
            if m:
                best += _to_float(m.group(0))
    return round(best, 2)

def _parse_extrusion(text: str) -> float:
    """
    Суммируем только числа:
      1) в строках, где есть 'экструз'/'экструдер';
      2) в следующих 1–2 строках, если они начинаются на мяг/тв (варианты: 'м', 'мягк', 'тв', 'твёрд', 'тв.').
    Игнорируем строки, начинающиеся на 'итого'/'всего' даже если они рядом.
    Никакого глобального поиска 'м'/'т' по всему тексту.
    """
    lines = [ln.rstrip().lower() for ln in text.splitlines()]
    total = 0.0

    extru_re = re.compile(r'экструз|экструдер', re.IGNORECASE)
    soft_re  = re.compile(r'^\W*(?:мягк|мяг\.?|м)\b', re.IGNORECASE)
    hard_re  = re.compile(r'^\W*(?:тв(?:ёрд|ерд)|тв\.?|т)\b', re.IGNORECASE)
    skip_sum = re.compile(r'^\W*(?:итого|всего)\b', re.IGNORECASE)

    i = 0
    while i < len(lines):
        line = lines[i]
        if extru_re.search(line) and not skip_sum.search(line):
            # числа прямо в строке экструзии
            total += _sum_numbers_in_line(line)
            # смотрим до двух нижних строк с мяг/тв
            look_ahead = 0
            j = i + 1
            while j < len(lines) and look_ahead < 2:
                nxt = lines[j]
                if skip_sum.search(nxt):
                    break
                if soft_re.search(nxt) or hard_re.search(nxt):
                    total += _sum_numbers_in_line(nxt)
                    look_ahead += 1
                    j += 1
                    continue
                break
        i += 1

    return round(total, 2)

def parse_message(text: str) -> dict:
    """
    Возвращает dict с найденными значениями.
    Суммирование идёт только по строкам, где встречается соответствующее слово.
    Ничего не тянем из соседних несвязанных строк (например, '7м 15000' вне блока экструзии).
    """
    # Для кейсов с разными регистрами и ё/е
    txt = text.replace('Ё', 'Е').replace('ё', 'е')

    res = {}

    # Паков / Вес — берём число из той же строки
    pak = _extract_number(txt, r'паков|паки|упаковка|упаковок')
    if pak:
        res["Паков"] = pak

    ves = _extract_number(txt, r'вес')
    if ves:
        res["Вес"] = ves

    # Пакетосварка и Флекса — суммируем числа в строках, где встречается слово
    # (если строк несколько, суммируем все)
    def sum_by_keyword(all_text: str, kw_pattern: str) -> float:
        total = 0.0
        kw = re.compile(kw_pattern, re.IGNORECASE)
        for raw in all_text.splitlines():
            line = raw.strip()
            if not line:
                continue
            if kw.search(line):
                total += _sum_numbers_in_line(line)
        return round(total, 2)

    paket = sum_by_keyword(txt, r'пакетосвар')
    if paket:
        res["Пакетосварка"] = paket

    flexa = sum_by_keyword(txt, r'флекс')
    if flexa:
        res["Флекса"] = flexa

    # Экструзия — специальная логика (строка экструзии + до 2 строк ниже с мяг/тв)
    if re.search(r'(экструзия|экструдер)', txt, re.IGNORECASE):
        ext = _parse_extrusion(text)  # важно: необработанный text с переносами
        if ext:
            res["Экструзия"] = ext
        else:
            # запасной вариант — число в той же строке, где упоминается экструзия/экструдер
            fallback = _extract_number(txt, r'экструзия|экструдер')
            if fallback:
                res["Экструзия"] = fallback

    return res
