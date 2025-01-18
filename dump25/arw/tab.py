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
    yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    delta = int(now - time_start)
    print(yellow % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")


def log_dump(tab):
    jsonname = Path(__file__).parent / "arw.json"
    # ---
    with open(jsonname, "w", encoding="utf-8") as outfile:
        ujson.dump(tab, outfile)
    # ---
    print("log_dump done")


def do_line(json1):
    # ---
    stats_tab["all_items"] += 1
    # ---
    # q = json1['id']
    sitelinks = json1.get("sitelinks", [])
    if not sitelinks:
        stats_tab["no_sitelinks"] += 1
        del json1
        return
    # ---
    arlink = "arwiki" in sitelinks
    # ---
    if not arlink:
        # عناصر بوصلات لغات بدون وصلة عربية
        stats_tab["sitelinks_no_ar"] += 1
        del json1, sitelinks
        return
    # ---
    # عناصر ويكي بيانات بها وصلة عربية
    stats_tab["all_ar_sitelinks"] += 1
    arlink_type = "pages"
    stats_tab[arlink_type]["count"] += 1
    # ---
    if arlink_type not in stats_tab["p31_main_tab"]:
        stats_tab["p31_main_tab"][arlink_type] = {}
    # ---
    p31x = "no"
    # ---
    claims = json1.get("claims", {})
    # ---
    if not claims:
        # صفحات دون أية خواص
        stats_tab["no_claims"] += 1
    # ---
    P31 = claims.get("P31", [])
    # ---
    if not P31:
        # صفحة بدون خاصية P31
        stats_tab["no_p31"] += 1
        # ---
        if len(claims) > 0:
            # خواص أخرى بدون خاصية P31
            stats_tab["other_claims_no_p31"] += 1
    # ---
    ar_desc = "ar" in json1.get("descriptions", [])
    # ---
    for p31x in P31:
        # ---
        if p31x in stats_tab["p31_main_tab"][arlink_type]:
            stats_tab["p31_main_tab"][arlink_type][p31x] += 1
        else:
            stats_tab["p31_main_tab"][arlink_type][p31x] = 1
        # ---
        if not ar_desc:
            # استخدام خاصية 31 بدون وصف عربي
            # ---
            if p31x not in stats_tab["Table_no_ar_lab"]:
                stats_tab["Table_no_ar_lab"][p31x] = 0
            # ---
            stats_tab["Table_no_ar_lab"][p31x] += 1
    # ---
    tat = ["labels", "descriptions", "aliases"]
    # ---
    for x in tat:
        if x not in json1:
            # دون عربي
            stats_tab[arlink_type][x]["no"] += 1
            continue
        # ---
        stats_tab[arlink_type][x]["yes"] += 1
        # ---
        # تسمية عربي
        if "ar" in json1[x]:
            stats_tab[arlink_type][x]["yesar"] += 1
        else:
            stats_tab[arlink_type][x]["noar"] += 1


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
    n = 0
    # ---
    for x in tqdm.tqdm(jsonfiles):
        lines = get_lines(x)
        # ---
        n += 1
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
                log_dump(stats_tab)
        # ---
        if n % 100 == 0:
            print(cc, time.time() - tt[1])
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
