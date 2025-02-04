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
sql_path = Dir / "claims_dump.db"
# ---
if not sql_path.exists():
    sql_path.touch()

most_path = Dir / "most_claims.json"

if not most_path.exists():
    most_path.write_text('{"q": "", "count": 0}')

most_data = json.loads(most_path.read_text())

start_time = time.time()


tabs = {}  # {"P31": {"Q5": 0}}


def print_memory():
    green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"
    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = naturalsize(usage, binary=True)
    delta = int(time.time() - start_time)
    print(green % "Memory usage:", purple % f"{usage}", f"time: to now {delta}")


def compare_most(most):
    # ---
    global most_data
    # ---
    if most["count"] > most_data["count"]:
        most_path.write_text(json.dumps(most))
        # ---
        most_data = most


def create_tables():
    conn = sqlite3.connect(sql_path)
    # ---
    table_create = """
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pid TEXT NOT NULL,
        qid TEXT NOT NULL,
        count INTEGER NOT NULL,
        UNIQUE(pid, qid)
    );
    """
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
    batch_size = 1000
    values = []
    # ---
    for pid, qids in tab.items():
        # print(table_name)
        # ----
        for qid, count in qids.items():
            if not qid or not pid or not count:
                # print(pid, qid, count)
                continue
            values.append((pid, qid, count))
            if len(values) >= batch_size:
                cursor.executemany(
                    """
                    INSERT INTO claims (pid, qid, count)
                    VALUES (?, ?, ?)
                    ON CONFLICT(pid, qid) DO UPDATE SET count = count + excluded.count;
                    """,
                    values,
                )
                values = []
                conn.commit()
    if values:
        cursor.executemany(
            """
            INSERT INTO claims (pid, qid, count)
            VALUES (?, ?, ?)
            ON CONFLICT(pid, qid) DO UPDATE SET count = count + excluded.count;
            """,
            values,
        )
        conn.commit()
    # ---
    conn.close()


def dump_lines(lines):
    # ---
    global tabs
    # ---
    _line = {
        "qid": "Q00",
        "claims": {"P31": ["Q5", "Q0"]},
    }
    # ---
    most = {"q": "", "count": 0}
    # ---
    for line in lines:
        # ---
        claims = line.get("claims", {})
        # ---
        _claims = {"P59": ["Q10519"], "P31": ["Q523", "Q67206691"], "P6259": ["Q1264450"]}
        # ---
        if len(claims) > most["count"]:
            most["count"] = len(claims)
            most["q"] = line["qid"]
        # ---
        # print(claims)
        # ---
        for pid, qids in claims.items():
            # ---
            if pid not in tabs:
                tabs[pid] = {}
            # ---
            for qid in qids:
                if qid not in tabs[pid]:
                    tabs[pid][qid] = 0
                # ---
                tabs[pid][qid] += 1
        # ---
        del claims, line
    # ---
    compare_most(most)


def main():
    # ---
    global tabs
    # ---
    create_tables()
    # ---
    dump_dir = Path(__file__).parent.parent / "parts"
    # ---
    files = [x for x in dump_dir.glob("*.json")]
    # ---
    nx = 0
    # ---
    for file in tqdm.tqdm(files):
        # ---
        nx += 1
        # ---
        with open(file, "r", encoding="utf-8") as f:
            lines = ujson.load(f)
        # ---
        # print(f"lines: {len(lines)}")
        # ---
        dump_lines(lines)
        # ---
        gc.collect()
        # ---
        if nx % 10 == 0:
            print_memory()
            sql_add_values(tabs)
            # ---
            del tabs
            # ---
            gc.collect()
            # ---
            tabs = {}  # {"P31": {"Q5": 0}}
        # ---
        if "break" in sys.argv:
            break


def test():
    conn = sqlite3.connect(sql_path)
    cursor = conn.cursor()
    # ---
    cursor.execute("SELECT * FROM claims ORDER BY count DESC LIMIT 1;")
    # ---
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()


if __name__ == "__main__":
    if "test" in sys.argv:
        test()
    else:
        main()
