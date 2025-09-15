"""

"""
import sqlite3
import os
import tqdm
import psutil
import gc
import ujson
import json
import time
import sys
from pathlib import Path
from humanize import naturalsize

Dir = Path(__file__).parent
sql_path = Dir / "dump.db"
# ---
if not sql_path.exists():
    sql_path.touch()

table_names = ["labels", "aliases", "descriptions", "sitelinks"]

most_path = Dir / "most.json"

if not most_path.exists():
    most_path.write_text("{}")

most_data = json.loads(most_path.read_text())

start_time = time.time()


def print_memory():
    green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"
    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = naturalsize(usage, binary=True)
    delta = int(time.time() - start_time)
    print(green % "Memory usage:", purple % f"{usage}", f"time: to now {delta}")


def compare_most(most):
    # ---
    change = False
    # ---
    for x in most:
        if x not in most_data:
            most_data[x] = {"q": "", "count": 0}
            change = True
        # ---
        if most[x]["count"] > most_data[x]["count"]:
            most_data[x] = most[x]
            change = True
    # ---
    if change:
        most_path.write_text(json.dumps(most_data))


def create_tables():
    conn = sqlite3.connect(sql_path)
    # ---
    for x in table_names:
        table_create = f"""
            CREATE TABLE IF NOT EXISTS {x} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                count INTEGER NOT NULL
            );"""
        # ---
        cursor = conn.cursor()
        cursor.execute(table_create)
        conn.commit()
    # ---
    conn.close()


def sql_add_values(tab):
    # ---
    conn = sqlite3.connect(sql_path)
    # ---
    cursor = conn.cursor()
    # ---
    for table_name, data in tab.items():
        # ---
        for code, count in data.items():
            # print(table_name)
            # ----
            cursor.execute(
                f"""
                    INSERT INTO {table_name} (code, count)
                    VALUES (?, ?)
                    ON CONFLICT(code)
                    DO UPDATE SET count = count + ?
                    """,
                (code, count, count),
            )
        # ---
        conn.commit()
    # ---
    conn.close()


def dump_lines(lines):
    # ---
    _line = {
        "qid": "Q00",
        "labels": ["el", "ay"],
        "aliases": ["el", "ay"],
        "descriptions": ["cy", "sk", "mk", "vls"],
        "sitelinks": ["arwiki", "enwiki"],
        "claims": {"P31": ["Q5", "Q0"]},
    }
    # ---
    most = {
        "labels": {"q": "", "count": 0},
        "descriptions": {"q": "", "count": 0},
        "aliases": {"q": "", "count": 0},
        "sitelinks": {"q": "", "count": 0},
        # "claims": {"q": "", "count": 0},
    }
    # ---
    tabs = {
        "labels": {"el": 0, "ay": 0},
        "aliases": {"el": 0, "ay": 0},
        "descriptions": {"el": 0, "ay": 0},
        "sitelinks": {"arwiki": 0, "enwiki": 0},
        # "claims": {"P31": ["Q5", "Q0"]},
    }
    # ---
    for line in lines:
        # ---
        for k in most:
            # ---
            for value in line.get(k, []):
                # ---
                if value not in tabs[k]:
                    tabs[k][value] = 0
                # ---
                tabs[k][value] += 1
            # ---
            if len(line.get(k, [])) > most[k]["count"]:
                most[k]["count"] = len(line.get(k, []))
                most[k]["q"] = line["qid"]
    # ---
    sql_add_values(tabs)
    # ---
    compare_most(most)


def main():
    # ---
    create_tables()
    # ---
    dump_dir = Path(__file__).parent.parent / "parts"
    # ---
    files = [x for x in dump_dir.glob("*.json")]
    # ---
    for file in tqdm.tqdm(files):
        # ---
        with open(file, "r", encoding="utf-8") as f:
            lines = ujson.load(f)
        # ---
        print(f"lines: {len(lines)}")
        # ---
        dump_lines(lines)
        # ---
        gc.collect()
        # ---
        print_memory()
        # ---
        if "break" in sys.argv:
            break


def test():
    conn = sqlite3.connect(sql_path)
    cursor = conn.cursor()
    # ---
    table_names = ["labels", "aliases", "descriptions", "sitelinks"]
    # ---
    # طباعة العناصر من قاعدة البيانات
    for table_name in table_names:
        print(f"table: {table_name}:")
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY count DESC LIMIT 1;")
        rows = cursor.fetchall()

        for row in rows:
            print(row)

    conn.close()


if __name__ == "__main__":
    if "test" in sys.argv:
        test()
    else:
        main()
