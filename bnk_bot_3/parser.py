
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
    Глобальный поиск мягких и твёрдых отходов в любом месте текста, даже если строки разделены.
    """
    m_patterns = r"(?:мягк(?:ие|ое)?|мягч|мяг\.?|[мm])"
    t_patterns = r"(?:тв(?:ёрд|ерд|в)?|тверд(?:ое|ые)?|тв\.?|[тt])"

    m_all = re.findall(rf"{m_patterns}\s*[:\-]?\s*([0-9]+[.,]?[0-9]*)", text, re.IGNORECASE)
    t_all = re.findall(rf"{t_patterns}\s*[:\-]?\s*([0-9]+[.,]?[0-9]*)", text, re.IGNORECASE)

    m_val = sum(_to_float(x) for x in m_all)
    t_val = sum(_to_float(x) for x in t_all)
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
