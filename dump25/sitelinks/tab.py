# -*- coding: utf-8 -*-
"""

python3 dump/sitelinks/tab.py


"""
import os
import psutil
import ujson
import tqdm
import time
from pathlib import Path

Dir = Path(__file__).parent.parent
# ---
parts_dir = Dir / "parts"
# ---
time_start = time.time()
print(f"time_start:{str(time_start)}")
# ---
tt = {1: time.time()}
# ---
tab = {
    "delta": 0,
    "done": 0,
    "no_sitelinks": 0,
    "file_date": "",
    "most_linked_item": "",
    "most_linked_item_count": 0,
    "All_items": 0,
    "sitelinks": {},
}


def print_memory():
    now = time.time()
    yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    delta = int(now - time_start)
    print(yellow % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")


def log_dump(tab):
    jsonname = Path(__file__).parent / "sitelinks.json"
    # ---
    with open(jsonname, "w", encoding="utf-8") as outfile:
        ujson.dump(tab, outfile)
    # ---
    print("log_dump done")


def do_line(json1):
    tab["done"] += 1
    tab["All_items"] += 1
    # ---
    _json1 = {
        "sitelinks": ["arwiki", "enwiki"],
    }
    # ---
    if len(json1.get("sitelinks", [])) == 0:
        tab["no_sitelinks"] += 1
    # ---
    if len(json1.get("sitelinks", {})) > tab["most_linked_item_count"]:
        tab["most_linked_item_count"] = len(json1.get("sitelinks", {}))
        tab["most_linked_item"] = json1["qid"]
        print(f"most_linked_item: {tab['most_linked_item']}, count: {tab['most_linked_item_count']}")
    # ---
    for code in json1.get("sitelinks", {}):
        if code not in tab["sitelinks"]:
            tab["sitelinks"][code] = 0
        tab["sitelinks"][code] += 1
    # ---
    del json1


def get_lines(x):
    with open(x, "r", encoding="utf-8") as f:
        for line in ujson.load(f):
            yield line


def read_lines():
    print("def read_lines():")
    # ---
    jsonfiles = list(parts_dir.glob("*.json"))
    print(f"all json files: {len(jsonfiles)}")
    # ---
    cc = 0
    # ---
    for x in tqdm.tqdm(jsonfiles):
        lines = get_lines(x)
        # ---
        for cc, line in enumerate(lines, start=cc):
            # ---
            do_line(line)
            # ---
            if cc % 1000000 == 0:
                print(cc, time.time() - tt[1])
                tt[1] = time.time()
                # print memory usage
                print_memory()
            # ---
            # if cc % 1000000 == 0: log_dump(tab)


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
