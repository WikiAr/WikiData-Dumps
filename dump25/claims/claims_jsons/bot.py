"""

"""
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
jsons_dir = Dir / "jsons"
# ---
if not jsons_dir.exists():
    jsons_dir.mkdir()

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


def sql_add_values(tab):
    # ---
    for pid, qids in tab.items():
        # ----
        pid_file = jsons_dir / f"{pid}.json"
        # ----
        pid_data = {}
        # ----
        if not pid_file.exists():
            pid_file.write_text("{}")
        else:
            pid_data = json.loads(pid_file.read_text())
        # ----
        for qid, count in qids.items():
            if not qid or not pid or not count:
                # print(pid, qid, count)
                continue
            # ---
            if qid not in pid_data:
                pid_data[qid] = 0
            # ---
            pid_data[qid] += count
        # ---
        pid_file.write_text(json.dumps(pid_data))


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
        if nx % 50 == 0:
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


if __name__ == "__main__":
    main()
