# -*- coding: utf-8 -*-
"""

python3 dump1/labels/tab_fixed.py


"""
import os
import psutil
import ujson
import tqdm
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dir_handler import dump_parts1_fixed, labels_results_dir

time_start = time.time()
print(f"time_start:{str(time_start)}")
# ---
tt = {1: time.time()}
# ---
tab = {
    "no": {
        "labels": 0,
        "descriptions": 0,
        "aliases": 0,
        "sitelinks": 0,
    },
    "most": {
        "labels": {"q": "", "count": 0},
        "descriptions": {"q": "", "count": 0},
        "aliases": {"q": "", "count": 0},
        "sitelinks": {"q": "", "count": 0},
    },
    "delta": 0,
    "done": 0,
    "file_date": "",
    "All_items": 0,
    "langs": {},
    "sitelinks": {},
}


def print_memory():
    now = time.time()
    green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    delta = int(now - time_start)
    print(green % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")


def log_dump(tab):
    jsonname = labels_results_dir / "labels_new.json"
    # ---
    with open(jsonname, "w", encoding="utf-8") as outfile:
        ujson.dump(tab, outfile)
    # ---
    print("log_dump done")


def do_line(json1):
    tab["done"] += json1.get("All_items", 0)
    tab["All_items"] += json1.get("All_items", 0)
    # ---
    for x in json1.get("no", {}):
        tab["no"][x] += json1["no"][x]
    # ---
    for x, v in json1.get("most", {}).items():
        if v["count"] > tab["most"][x]["count"]:
            tab["most"][x]["count"] = v["count"]
            tab["most"][x]["q"] = v["q"]
    # ---
    for code, count in json1.get("sitelinks", {}).items():
        if code not in tab["sitelinks"]:
            tab["sitelinks"][code] = 0
        tab["sitelinks"][code] += count
    # ---
    for code, vals in json1.get("langs", {}).items():
        if code not in tab["langs"]:
            tab["langs"][code] = {"labels": 0, "descriptions": 0, "aliases": 0}
        for x, v in vals.items():
            tab["langs"][code][x] += v
    # ---
    del json1


def get_lines(x):
    with open(x, "r", encoding="utf-8") as f:
        return ujson.load(f)


def read_lines():
    print("def read_lines():")
    # ---
    jsonfiles = list(dump_parts1_fixed.glob("*.json"))
    print(f"all json files: {len(jsonfiles)}")
    # ---
    current_count = 0
    # ---
    for x in tqdm.tqdm(jsonfiles):
        # ---
        current_count += 1
        # ---
        line = get_lines(x)
        # ---
        do_line(line)
        # ---
        if current_count % 500 == 0:
            print(current_count, time.time() - tt[1])
            tt[1] = time.time()
            # print memory usage
            print_memory()


def read_file():
    # ---
    print(f"file date: {tab['file_date']}")
    # ---
    read_lines()
    # ---
    print(f"read all lines: {tab['done']}")
    # ---
    end = time.time()
    # ---
    delta = int(end - time_start)
    tab["delta"] = f"{delta:,}"
    # ---
    log_dump(tab)
    # ---
    print(f"read_file: done in {tab['delta']}")


if __name__ == "__main__":
    read_file()
