# parse.py
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
    Ищет первое число в каждой строке, где встречается один из шаблонов (patterns).
    Если таких строк несколько — суммируем найденные числа.
    """
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
    Экструзия считается ТОЛЬКО:
      1) из строки, где есть 'экструз' или 'экструдер';
      2) из следующих ниже строк (до 6 непустых, пустые можно пропускать),
         которые начинаются на мяг/тв (варианты: 'м', 'мягк', 'тв', 'твёрд', 'тв.').
    'итого/всего' блок экструзии прерывают и не суммируются.
    Любой другой раздел (напр. 'Флекса', 'Окрашено') — завершает блок.
    """
    lines = [ln.rstrip() for ln in text.splitlines()]
    total = 0.0

    extru_re = re.compile(r'(экструз|экструд)', re.IGNORECASE)         # экструзия/экструдер
    soft_re  = re.compile(r'^\W*(?:мягк|мяг\.?|м)\b', re.IGNORECASE)   # мяг, мягкие, м
    hard_re  = re.compile(r'^\W*(?:тв(?:ёрд|ерд)|тв\.?|т)\b', re.IGNORECASE)  # тв, твердые, т
    skip_sum = re.compile(r'^\W*(?:итого|всего)\b', re.IGNORECASE)

    i = 0
    while i < len(lines):
        line_l = lines[i].lower()
        if extru_re.search(line_l) and not skip_sum.search(line_l):
            # Числа прямо в строке экструзии (если есть)
            total += _sum_numbers_in_line(lines[i])

            # Смотрим вниз до 6 непустых строк, пропуская пустые
            nonempty_seen = 0
            j = i + 1
            while j < len(lines) and nonempty_seen < 6:
                nxt = lines[j]
                nxt_l = nxt.lower()

                if not nxt.strip():
                    j += 1
                    continue  # пустую строку просто пропускаем

                nonempty_seen += 1

                if skip_sum.search(nxt_l):
                    break  # дошли до 'итого/всего' — стоп блока

                if soft_re.search(nxt_l) or hard_re.search(nxt_l):
                    total += _sum_numbers_in_line(nxt)
                    j += 1
                    continue

                # Любой другой раздел — завершаем блок экструзии
                break
        i += 1

    return round(total, 2)

def parse_message(text: str) -> dict:
    """
    Возвращает dict с найденными значениями.
    Суммирование идёт только по строкам, где встречается соответствующее слово.
    Ничего не тянем из несвязанных строк (например, '7м 15000' вне блока экструзии).
    """
    # Нормализуем ё/е
    txt = text.replace('Ё', 'Е').replace('ё', 'е')

    res = {}

    # Паков / Вес — число из соответствующих строк (суммируем, если несколько строк)
    pak = _extract_number(txt, r'паков|паки|упаковка|упаковок')
    if pak:
        res["Паков"] = pak

    ves = _extract_number(txt, r'вес')
    if ves:
        res["Вес"] = ves

    # Пакетосварка и Флекса — сумма чисел во всех строках с этими словами
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

    # Экструзия — специальная логика (строка экструзии + до 6 непустых строк ниже с мяг/тв)
    if re.search(r'(экструз|экструд)', txt, re.IGNORECASE):
        ext = _parse_extrusion(text)  # важно: исходный текст с переносами
        if ext:
            res["Экструзия"] = ext
        else:
            # запасной вариант — число в той же строке, где упоминается экструзия/экструдер
            fallback = _extract_number(txt, r'экструзия|экструдер')
            if fallback:
                res["Экструзия"] = fallback

    return res
