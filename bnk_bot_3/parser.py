
import re

def _to_float(s):
    try:
        return float(str(s).replace(",", "."))
    except Exception:
        return 0.0


def _extract_number(text, patterns):
    m = re.search(rf"(?:{patterns})\s*[:\-]?\s*([0-9]+[.,]?[0-9]*)", text, re.IGNORECASE)
    return _to_float(m.group(1)) if m else 0.0


def _parse_extrusion(text):
    """
    Парсит экструзию (экструзия|экструдер), включая сокращения и синонимы для мягких и твёрдых отходов.
    Поддержка:
    - м, мягк, мягкие, мягкое, мяг., мягч, m
    - т, тверд, твёрд, твердое, твёрдое, твер., тв, t
    """
    m_patterns = r"[мm]|мяг(?:к|кие|кое|ч|\.|\-)?|мягк"
    t_patterns = r"[тt]|тв(?:ёрд|ерд|ёрдое|ердое|в)?|тверд(?:ое|ые)?|тв"

    m_match = re.search(rf"(?:экструзия|экструдер).*?{m_patterns}\s*[:\-]?\s*([0-9]+[.,]?[0-9]*)", text, re.IGNORECASE)
    t_match = re.search(rf"(?:экструзия|экструдер).*?{t_patterns}\s*[:\-]?\s*([0-9]+[.,]?[0-9]*)", text, re.IGNORECASE)

    m_val = _to_float(m_match.group(1)) if m_match else 0.0
    t_val = _to_float(t_match.group(1)) if t_match else 0.0
    return round(m_val + t_val, 2)


def parse_message(text):
    txt = text.lower()
    result = {}

    pak = _extract_number(txt, r"паков|паки|упаковка|упаковок")
    if pak:
        result["Паков"] = pak

    ves = _extract_number(txt, r"вес")
    if ves:
        result["Вес"] = ves

    paketo = _extract_number(txt, r"пакетосварка")
    if paketo:
        result["Пакетосварка"] = paketo

    flexa = _extract_number(txt, r"флекса|флексография|флексо|фоекса|флекс")
    if flexa:
        result["Флекса"] = flexa

    if re.search(r"(экструзия|экструдер)", txt, re.IGNORECASE):
        ext = _parse_extrusion(txt)
        if ext:
            result["Экструзия"] = ext
        else:
            ext_fallback = _extract_number(txt, r"экструзия|экструдер")
            if ext_fallback:
                result["Экструзия"] = ext_fallback

    return result
