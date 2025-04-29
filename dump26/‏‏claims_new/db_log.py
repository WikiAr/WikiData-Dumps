# -*- coding: utf-8 -*-
"""

"""
import os
import json
import tqdm
import sqlite3
from pathlib import Path

main_path = Path(__file__).parent

db_path = f"{str(main_path)}/wd_logs.db"

db_path_main = {1: str(db_path)}

print("db_path", db_path_main[1])


def db_commit(query, params=[], many=False):
    try:
        with sqlite3.connect(db_path_main[1]) as conn:
            cursor = conn.cursor()
            if many:
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)
        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"init_db Database error: {e}")
        return e


def init_db():
    # ---
    query = """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pid TEXT NOT NULL,
        qid TEXT NOT NULL,
        counts INTEGER DEFAULT 1,
        UNIQUE(pid, qid)
    );"""
    # ---
    db_commit(query)


def fetch_all(query, params=[], fetch_one=False):
    try:
        with sqlite3.connect(db_path_main[1]) as conn:
            # Set row factory to return rows as dictionaries
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Execute the query
            cursor.execute(query, params)

            # Fetch results
            if fetch_one:
                row = cursor.fetchone()
                logs = dict(row) if row else None  # Convert to dictionary
            else:
                rows = cursor.fetchall()
                logs = [dict(row) for row in rows]  # Convert all rows to dictionaries

    except sqlite3.Error as e:
        print(f"Database error in view_logs: {e}")
        if "no such table" in str(e):
            init_db()
        logs = []

    return logs


def log_one(pid, qid, counts):
    # ---
    result = db_commit(
        """
        INSERT INTO logs (pid, qid, counts)
        VALUES (?, ?, ?)
        ON CONFLICT(pid, qid) DO UPDATE SET
            counts = counts + excluded.counts
        """,
        (pid, qid, counts),
    )
    # ---
    if result is not True:
        print(f"Error logging request: {result}")
        if "no such table" in str(result):
            init_db()
    # ---
    return result


def add_params(query, params, qid="", pid=""):
    # ---
    if not isinstance(params, list):
        params = list(params)
    # ---
    if qid:
        query += " WHERE qid = ?"
        params.append(qid)
    # ---
    if pid:
        WHERE = "WHERE" if not qid else "AND"
        query += f" {WHERE} qid pid ?"
        params.append(pid)
    # ---
    return query, params


def sum_counts(qid="", pid=""):
    # ---
    query = "select sum(counts) as count_all from logs"
    # ---
    params = []
    # ---
    query, params = add_params(query, params, qid=qid, pid=pid)
    # ---
    result = fetch_all(query, params, fetch_one=True)
    # ---
    print("result", result)
    # ---
    result = result["count_all"] or 0
    # ---
    return result


def get_response_status():
    # ---
    query = "select qid, count(qid) as numbers from logs group by qid having count(*) > 2"
    # ---
    result = fetch_all(query, ())
    # ---
    result = [row['qid'] for row in result]
    # ---
    return result


def count_all(qid="", pid=""):
    # ---
    query = "SELECT COUNT(*) FROM logs"
    # ---
    params = []
    # ---
    query, params = add_params(query, params, qid=qid, pid=pid)
    # ---
    result = fetch_all(query, params, fetch_one=True)
    # ---
    if not result:
        return 0
    # ---
    if isinstance(result, list):
        result = result[0]
    # ---
    total_logs = result["COUNT(*)"]
    # ---
    return total_logs


def get_logs(per_page=10, offset=0, order="DESC", order_by="counts", qid="", pid=""):
    # ---
    if order not in ["ASC", "DESC"]:
        order = "DESC"
    # ---
    query = "SELECT * FROM logs "
    # ---
    params = []
    # ---
    query, params = add_params(query, params, qid=qid, pid=pid)
    # ---
    query += f"ORDER BY {order_by} {order} LIMIT ? OFFSET ?"
    # ---
    params.extend([per_page, offset])
    # ---
    logs = fetch_all(query, params)
    # ---
    return logs


def one_item(pid, qids):
    # ---
    for qid, counts in qids.items():
        db_commit(
            """
        INSERT INTO logs (pid, qid, counts)
        VALUES (?, ?, ?)
        ON CONFLICT(pid, qid) DO UPDATE SET
            counts = counts + excluded.counts
        """,
            (pid, qid, counts),
        )


def one_item_qids(pid, qids):
    batch_size = 5000
    # ---
    items = list(qids.items())
    # ---
    query = """
        INSERT INTO logs (pid, qid, counts)
        VALUES (?, ?, ?)
        ON CONFLICT(pid, qid) DO UPDATE SET
            counts = counts + excluded.counts
        """
    # ---
    # print(f"{len(items)=:,}, {batch_size=:,}")
    # ---
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        data = [(pid, qid, counts) for qid, counts in batch]

        db_commit(query, data, many=True)


def log_items(properties_qids):

    for pid, qids in tqdm.tqdm(properties_qids.items(), desc=f"log_items: {len(properties_qids)=:,}"):
        one_item_qids(pid, qids)


def write_it():

    file = Path(__file__).parent / "jsons/claims.json"
    # ---
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        # ---
        for pid, qids in data.items():
            one_item_qids(pid, qids)


    # ---
if __name__ == "__main__":
    # python3 I:\core\bots\dump_core\dump26\claims_new\db_log.py
    init_db()
    # ---
    pid = "P6216"
    qids = {"Q50423863": 10, "Q19652": 5, "Q99263261": 0, "Q88088423": 0, "Q59496158": 0}
    # ---
    one_item(pid, qids)
    # ---
    # write_it()
    # ---
    print("count_all", count_all(qid="no_result"))
    # ---
    print("get_response_status", get_response_status())
    # ---
    print("get_logs:")
    for x in get_logs(qid=""):
        # {'id': 1, 'pid': 'P6216', 'qid': 'Q50423863', 'counts': 3369}
        print(x)
    # ---
