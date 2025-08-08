import os
from datetime import datetime

from openpyxl import Workbook, load_workbook

# ──────────────────────────────────────────────────────────────────────────────
# Папки для данных и графиков
# ──────────────────────────────────────────────────────────────────────────────
DATA_DIR = "/config/bnk_bot/data"
GRAPHS_DIR = "/config/bnk_bot/graphs"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)


def get_file_path():
    """Путь к Excel-файлу текущего месяца: /config/bnk_bot/data/YYYY-MM.xlsx"""
    return os.path.join(DATA_DIR, f"{datetime.now().strftime('%Y-%m')}.xlsx")


def save_entry(date, user, values):
    """
    Сохраняем одну строку в Excel.
    Колонки: Дата | Имя | Паков | Вес | Пакетосварка | Флекса | Экструзия | Итого
    """
    file_path = get_file_path()

    if os.path.exists(file_path):
        wb = load_workbook(file_path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["Дата", "Имя", "Паков", "Вес", "Пакетосварка", "Флекса", "Экструзия", "Итого"])

    ws.append([
        date.strftime('%Y-%m-%d %H:%M'),
        user,
        values.get("Паков", 0),
        values.get("Вес", 0),
        values.get("Пакетосварка", 0),
        values.get("Флекса", 0),
        values.get("Экструзия", 0),
        values.get("Итого", 0),
    ])

    wb.save(file_path)


def get_csv_file():
    """Возвращает путь к текущему Excel-файлу."""
    return get_file_path()


def generate_stats(stats):
    """
    Текстовая сводка /stats по пользователям.
    Ожидается структура:
    user_stats[user] = {
        'Паков': float, 'Вес': float, 'Пакетосварка': float, 'Флекса': float,
        'Экструзия': float, 'Итого': float, 'Смен': int
    }
    """
    lines = ["📊 Статистика по пользователям:"]
    for user, data in stats.items():
        lines.append(
            f"{user}:\n"
            f"  🧃 Паков: {data['Паков']:.2f} шт\n"
            f"  🏋️‍♂️ Вес: {data['Вес']:.2f} кг\n"
            f"  ❌ Пакетосварка: {data['Пакетосварка']:.2f} кг\n"
            f"  🎨 Флекса: {data['Флекса']:.2f} кг\n"
            f"  🧵 Экструзия: {data['Экструзия']:.2f} кг\n"
            f"  📦 Итого отходов: {data['Итого']:.2f} кг\n"
            f"  🗓 Смен: {int(data.get('Смен', 0))}"
        )
    return "\n\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Графики для /graf
# ──────────────────────────────────────────────────────────────────────────────
def _ensure_matplotlib():
    """
    Ленивая загрузка matplotlib, чтобы не падать при импорте,
    если модуль не установлен (но он должен быть в requirements.txt).
    """
    try:
        import matplotlib.pyplot as plt  # noqa
        return True
    except Exception as e:
        print(f"[WARN] matplotlib не найден или не загрузился: {e}")
        return False


def generate_graphs(user_stats):
    """
    Строит 3 графика (бар-чарты) по пользователям и возвращает список путей к PNG:
      1) Паков по пользователям
      2) Вес по пользователям
      3) Итого отходов по пользователям
    """
    if not _ensure_matplotlib():
        return []

    import matplotlib.pyplot as plt  # требование: не задавать стили и цвета

    users = list(user_stats.keys())
    if not users:
        return []

    pakov_vals = [float(user_stats[u].get('Паков', 0.0)) for u in users]
    ves_vals   = [float(user_stats[u].get('Вес', 0.0)) for u in users]
    waste_vals = [float(user_stats[u].get('Итого', 0.0)) for u in users]

    out_files = []

    # 1) Паков
    fig = plt.figure()
    plt.bar(users, pakov_vals)
    plt.title("Паков по пользователям")
    plt.xlabel("Пользователи")
    plt.ylabel("Паков, шт")
    plt.xticks(rotation=30, ha='right')
    path1 = os.path.join(GRAPHS_DIR, "pakov_by_user.png")
    fig.tight_layout()
    fig.savefig(path1)
    plt.close(fig)
    out_files.append(path1)

    # 2) Вес
    fig = plt.figure()
    plt.bar(users, ves_vals)
    plt.title("Вес по пользователям")
    plt.xlabel("Пользователи")
    plt.ylabel("Вес, кг")
    plt.xticks(rotation=30, ha='right')
    path2 = os.path.join(GRAPHS_DIR, "ves_by_user.png")
    fig.tight_layout()
    fig.savefig(path2)
    plt.close(fig)
    out_files.append(path2)

    # 3) Итого отходов
    fig = plt.figure()
    plt.bar(users, waste_vals)
    plt.title("Итого отходов по пользователям")
    plt.xlabel("Пользователи")
    plt.ylabel("Отходы, кг")
    plt.xticks(rotation=30, ha='right')
    path3 = os.path.join(GRAPHS_DIR, "waste_by_user.png")
    fig.tight_layout()
    fig.savefig(path3)
    plt.close(fig)
    out_files.append(path3)

    return out_files
