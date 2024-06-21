"""
python3 /data/project/himo/bots/dump_core/dump2/labels/do_tab.py
python3 bots/dump_core/dump2/labels/do_tab.py
python3 core8/pwb.py dump2/labels/do_tab test
python3 core8/pwb.py dump2/labels/do_tab test nosave

"""
import os
import psutil
import ujson
import sys
import time

# ---
time_start = time.time()
print(f"time_start:{str(time_start)}")
# ---
jsons_dir = "/data/project/himo/bots/dump_core/dump2/jsons/"
# ---
items_file = f"{jsons_dir}/items.json"
jsonname = f"{jsons_dir}/labels.json"
# ---
if "test" in sys.argv:
    items_file = f"{jsons_dir}/items_test.json"
    jsonname = f"{jsons_dir}/labels_test.json"
# ---
tt = {1: time.time()}
# ---
tab = {
    "delta": 0,
    "done": 0,
    "file_date": "",
    "All_items": 0,
    "langs": {},
}


def print_memory():
    yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    print(yellow % "Memory usage:", purple % f"{usage} MB")


def log_dump(tab):
    if "nodump" in sys.argv:
        return
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
        for code in json1.get(x, {}):
            if code not in tab["langs"]:
                tab["langs"][code] = {"labels": 0, "descriptions": 0, "aliases": 0}
            tab["langs"][code][x] += 1
    # ---
    del json1


def get_lines():
    with open(items_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if line.strip():
            yield ujson.loads(line.strip())


def read_lines():
    print("def read_lines():")
    # ---
    lines = get_lines()
    # ---
    for cc, line in enumerate(lines):
        # ---
        do_line(line)
        # ---
        if cc % 100000 == 0:
            print(cc, time.time() - tt[1])
            tt[1] = time.time()
            # print memory usage
            print_memory()
        # ---
        if cc % 1000000 == 0:
            log_dump(tab)


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
    print(f"read_file: done in {tab['delta']}")
    # ---
    log_dump(tab)
    # ---


if __name__ == "__main__":
    read_file()
