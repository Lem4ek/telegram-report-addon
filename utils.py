import os
import csv
from datetime import datetime
import pandas as pd

DATA_DIR = "/config/bnk_bot/data"
USERS_FILE = "/config/bnk_bot/users.csv"

def get_csv_path():
    now = datetime.now()
    filename = f"{now.year}_{now.month:02}.csv"
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, filename)

def extract_data(text):
    lines = text.strip().split('\n')
    result = {"Паков": 0, "Вес": 0, "Отходы": 0}
    for line in lines:
        line = line.strip().lower()
        if "паков" in line:
            result["Паков"] += int(''.join(filter(str.isdigit, line)))
        elif "вес" in line:
            result["Вес"] += int(''.join(filter(str.isdigit, line)))
        elif "итого" in line:
            result["Отходы"] += int(''.join(filter(str.isdigit, line)))
    return result

def append_to_csv(data, username):
    path = get_csv_path()
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), username, data["Паков"], data["Вес"], data["Отходы"]])

def export_csv():
    return get_csv_path()

def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    return pd.DataFrame(columns=["username"])

def save_users(user):
    df = load_users()
    if user.username not in df["username"].values:
        df.loc[len(df)] = [user.username]
        df.to_csv(USERS_FILE, index=False)

def get_stats():
    df = pd.read_csv(get_csv_path(), header=None, names=["date", "user", "Паков", "Вес", "Отходы"])
    if df.empty:
        return "Нет данных"
    summary = df.groupby("user")[["Паков", "Вес", "Отходы"]].sum()
    return summary.to_string()

def reset_all_data():
    path = get_csv_path()
    if os.path.exists(path):
        os.remove(path)