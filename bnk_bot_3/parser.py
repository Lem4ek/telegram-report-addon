import re

# 1 500, 1392,2, 16.4, 0.9, 12 и т.п.
NUM_RE = re.compile(r'(?:(?:\d{1,3}(?:[ \u00A0]\d{3})+|\d+)(?:[.,]\d+)?)')

SECTION_STOP_RE = re.compile(
    r'(?:^|\b)(паков|вес|флекс|пакетосвар|окраш|итого|всего)\b',
    re.IGNORECASE
)

def _to_float(s: str) -> float:
    s = str(s).replace('\u00A0', '').replace(' ', '').replace(',', '.')
    try:
        return float(s)
    except Exception:
        return 0.0

def _sum_numbers_in_line(line: str) -> float:
    return sum(_to_float(m.group(0)) for m in NUM_RE.finditer(line))

def _extract_number(text: str, patterns: str) -> float:
    """Сумма первых чисел в строках, где встречается один из patterns."""
    pat = re.compile(rf'(?:{patterns})', re.IGNORECASE)
    total = 0.0
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if pat.search(line):
            m = re.search(r'([0-9]{1,3}(?:[ \u00A0]\d{3})+|\d+)(?:[.,]\d+)?', line)
            if m:
                total += _to_float(m.group(0))
    return round(total, 2)

def _parse_extrusion(text: str) -> float:
    """
    Экструзия = числа:
      • в строке с 'экструз'/'экструдер'
      • + в следующих до 8 непустых строках (пустые пропускаем), если в строке встречается 'мяг' или 'тв'
    Блок обрывается, если встречаем другой раздел (флекса/пакетосварка/окрашено/паков/вес/итого/всего).
    """
    lines = [ln.rstrip() for ln in text.splitlines()]
    total = 0.0

    extru_re = re.compile(r'(экструз|экструд)', re.IGNORECASE)
    # Разрешаем не только начало строки, но и "… мягкие 14 …", "… т 0.9"
    soft_re  = re.compile(r'(?:^|\W)(мягк\w*|м\b)', re.IGNORECASE)
    hard_re  = re.compile(r'(?:^|\W)(тв(?:ёрд|ерд)\w*|тв\.?|т\b)', re.IGNORECASE)

    i = 0
    while i < len(lines):
        line = lines[i]
        low = line.lower()
        if extru_re.search(low) and not SECTION_STOP_RE.search(low):
            # числа прямо в строке экструзии (если есть)
            total += _sum_numbers_in_line(line)

            nonempty_seen = 0
            j = i + 1
            while j < len(lines) and nonempty_seen < 8:
                nxt = lines[j]
                if not nxt.strip():
                    j += 1
                    continue  # пустые строки пропускаем

                nonempty_seen += 1
                nxt_low = nxt.lower()

                # если пошёл другой раздел — выходим из блока
                if SECTION_STOP_RE.search(nxt_low):
                    break

                # "мяг"/"тв" — суммируем числа
                if soft_re.search(nxt_low) or hard_re.search(nxt_low):
                    total += _sum_numbers_in_line(nxt)
                    j += 1
                    continue

                # не мяг/тв и не пусто — это уже другой контент → выходим
                break
        i += 1

    return round(total, 2)

def parse_message(text: str) -> dict:
    """Парсинг отчёта по строкам. Ничего не тянем из несвязанных блоков."""
    txt = text.replace('Ё', 'Е').replace('ё', 'е')

    res = {}

    pak = _extract_number(txt, r'паков|паки|упаковка|упаковок')
    if pak:
        res["Паков"] = pak

    ves = _extract_number(txt, r'вес')
    if ves:
        res["Вес"] = ves

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

    if re.search(r'(экструз|экструд)', txt, re.IGNORECASE):
        ext = _parse_extrusion(text)  # исходный текст с переносами
        if ext:
            res["Экструзия"] = ext
        else:
            fallback = _extract_number(txt, r'экструзия|экструдер')
            if fallback:
                res["Экструзия"] = fallback

    return res
