# -*- coding: utf-8 -*-
"""

python3 tab.py

python3 dump/arw/tab.py

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
stats_tab = {
    "all_items": 0,
    "all_ar_sitelinks": 0,
    "no_sitelinks": 0,
    "sitelinks_no_ar": 0,
    "no_p31": 0,
    "no_claims": 0,
    "other_claims_no_p31": 0,
    "Table_no_ar_lab": {},
    "p31_main_tab": {"pages": {}},
    "delta": 0,
    "pages": {
        "count": 0,
        "labels": {"yes": 0, "no": 0, "yesar": 0, "noar": 0},
        "descriptions": {"yes": 0, "no": 0, "yesar": 0, "noar": 0},
        "aliases": {"yes": 0, "no": 0, "yesar": 0, "noar": 0},
    },
}


def print_memory():
    now = time.time()
    green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    delta = int(now - time_start)
    print(green % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")


def log_dump(tab):
    jsonname = Path(__file__).parent / "arw.json"
    # ---
    with open(jsonname, "w", encoding="utf-8") as outfile:
        ujson.dump(tab, outfile)
    # ---
    print("log_dump done")

def do_line(json1):
    stats_tab["all_items"] += 1

    sitelinks = json1.get("sitelinks", [])
    if not sitelinks:
        stats_tab["no_sitelinks"] += 1
        del json1
        return

    if "arwiki" not in sitelinks:
        # عناصر بوصلات لغات بدون وصلة عربية
        stats_tab["sitelinks_no_ar"] += 1
        del json1, sitelinks
        return

    # عناصر ويكي بيانات بها وصلة عربية
    stats_tab["all_ar_sitelinks"] += 1
    arlink_type = "pages"
    stats_tab[arlink_type]["count"] += 1

    stats_tab["p31_main_tab"].setdefault(arlink_type, {})

    claims = json1.get("claims", {})

    if not claims:
        # صفحات دون أية خواص
        stats_tab["no_claims"] += 1
    else:
        P31 = claims.get("P31", [])
        if not P31:
            # صفحة بدون خاصية P31
            stats_tab["no_p31"] += 1
            if claims:
                # خواص أخرى بدون خاصية P31
                stats_tab["other_claims_no_p31"] += 1

        ar_desc = "ar" in json1.get("descriptions", [])

        for p31x in P31:
            stats_tab["p31_main_tab"][arlink_type].setdefault(p31x, 0)
            stats_tab["p31_main_tab"][arlink_type][p31x] += 1

            if not ar_desc:
                # استخدام خاصية 31 بدون وصف عربي
                stats_tab["Table_no_ar_lab"].setdefault(p31x, 0)
                stats_tab["Table_no_ar_lab"][p31x] += 1

    for field in ["labels", "descriptions", "aliases"]:
        field_data = json1.get(field, {})
        if not field_data:
            # دون عربي
            stats_tab[arlink_type][field]["no"] += 1
        else:
            stats_tab[arlink_type][field]["yes"] += 1
            # تسمية عربي
            if "ar" in field_data:
                stats_tab[arlink_type][field]["yesar"] += 1
            else:
                stats_tab[arlink_type][field]["noar"] += 1


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
    current_count = 0
    # ---
    n = 0
    # ---
    for x in tqdm.tqdm(jsonfiles):
        lines = get_lines(x)
        # ---
        n += 1
        # ---
        for current_count, line in enumerate(lines, start=current_count):
            # ---
            do_line(line)
            # ---
            if current_count % 1000000 == 0:
                print(current_count, time.time() - tt[1])
                tt[1] = time.time()
                # print memory usage
                print_memory()
                log_dump(stats_tab)
        # ---
        if n % 100 == 0:
            print(current_count, time.time() - tt[1])
            tt[1] = time.time()
            # print memory usage
            print_memory()
            log_dump(stats_tab)


def read_file():
    # ---
    read_lines()
    # ---
    print(f"read all lines: {stats_tab['all_items']}")
    # ---
    end = time.time()
    # ---
    delta = int(end - time_start)
    stats_tab["delta"] = f"{delta:,}"
    # ---
    log_dump(stats_tab)
    # ---
    print(f"read_file: done in {stats_tab['delta']}")


if __name__ == "__main__":
    read_file()
