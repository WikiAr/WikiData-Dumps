# -*- coding: utf-8 -*-
"""

python3 dump/labels/tab.py


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
    "no": {
        "labels": 0,
        "descriptions": 0,
        "aliases": 0,
    },
    "most": {
        "labels": {"q": "", "count": 0},
        "descriptions": {"q": "", "count": 0},
        "aliases": {"q": "", "count": 0},
    },
    "delta": 0,
    "done": 0,
    "file_date": "",
    "All_items": 0,
    "langs": {},
}


def print_memory():
    now = time.time()
    yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    delta = int(now - time_start)
    print(yellow % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")


def log_dump(tab):
    jsonname = Path(__file__).parent / "labels.json"
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
        "labels": ["el", "ay"],
        "aliases": ["el", "ay"],
        "descriptions": ["cy", "sk", "mk", "vls"],
    }
    # ---
    tats = ["labels", "descriptions", "aliases"]
    # ---
    for x in tats:
        # ---
        ta_o = json1.get(x, {})
        # ---
        if len(ta_o) == 0:
            tab["no"][x] += 1
            continue
        # ---
        if len(ta_o) > tab["most"][x]["count"]:
            tab["most"][x]["count"] = len(ta_o)
            tab["most"][x]["q"] = json1["qid"]
            print(f"most {x}: {json1['qid']}, count: {len(ta_o)}")
        # ---
        for code in ta_o:
            if code not in tab["langs"]:
                tab["langs"][code] = {"labels": 0, "descriptions": 0, "aliases": 0}
            tab["langs"][code][x] += 1
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
    # ---


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
