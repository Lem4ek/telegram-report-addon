import re

def _to_float(s):
    try:
        return float(str(s).replace(",", "."))
    except Exception:
        return 0.0


def _extract_number(text, patterns):
    """
    Ищет первое число после любого из ключевых слов из patterns (регекс-строка с вариантами).
    Например: patterns="паков|паки|упаковка"
    Возвращает float (включая десятичные).
    """
    m = re.search(rf"(?:{patterns})\s*[:\-]?\s*([0-9]+[.,]?[0-9]*)", text, re.IGNORECASE)
    return _to_float(m.group(1)) if m else 0.0


def _parse_extrusion(text):
    """
    Парсит экструзию (экструзия|экструдер), поддерживает:
      - 'м65.5', 'м 65.5', 'м:65,5', 'м-65.5'
      - 'т12', 'т 0.6', 'т-12.8'
    Возвращает сумму мягких и твёрдых (float).
    """
    # общий блок, допускаем любые символы между ключом и числом
    m_match = re.search(r"(?:экструзия|экструдер).*?[мm]\s*[:\-]?\s*([0-9]+[.,]?[0-9]*)", text, re.IGNORECASE)
    t_match = re.search(r"(?:экструзия|экструдер).*?[тt]\s*[:\-]?\s*([0-9]+[.,]?[0-9]*)", text, re.IGNORECASE)

    m_val = _to_float(m_match.group(1)) if m_match else 0.0
    t_val = _to_float(t_match.group(1)) if t_match else 0.0
    return round(m_val + t_val, 2)


def parse_message(text):
    """
    Возвращает словарь только с найденными ключами:
      Паков, Вес, Пакетосварка, Флекса, Экструзия
    Никакой дополнительной фильтрации тут нет — фильтр по 'вес/итого'
    делает main.py (чтобы не дублировать логику).
    """
    txt = text.lower()

    result = {}

    # Паков (синонимы)
    pak = _extract_number(txt, r"паков|паки|упаковка|упаковок")
    if pak:
        result["Паков"] = pak

    # Вес
    ves = _extract_number(txt, r"вес")
    if ves:
        result["Вес"] = ves

    # Пакетосварка
    paketo = _extract_number(txt, r"пакетосварка")
    if paketo:
        result["Пакетосварка"] = paketo

    # Флекса (учтём 'фоекса' как опечатку + 'флексография')
    flexa = _extract_number(txt, r"флекса|флексография|флексо|фоекса|флекс")
    if flexa:
        result["Флекса"] = flexa

    # Экструзия / Экструдер
    if re.search(r"(экструзия|экструдер)", txt, re.IGNORECASE):
        ext = _parse_extrusion(txt)
        if ext:
            result["Экструзия"] = ext
        else:
            # запасной вариант: просто число после слова
            ext_fallback = _extract_number(txt, r"экструзия|экструдер")
            if ext_fallback:
                result["Экструзия"] = ext_fallback

    return result
