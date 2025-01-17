"""
https://hub-paws.wmcloud.org/user/Mr.%20Ibrahem/lab/tree/dump/claims/tab.py

python3 dump/claims/tab.py

python3 /data/project/himo/bots/dump_core/dump25/claims/tab.py

https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2

"""
import os
import psutil
import ujson
import tqdm
import time
from pathlib import Path

Dir = Path(__file__).parent.parent
# ---
dump_dir = Dir
parts_dir = Dir / "parts"
# ---
tt = {1: time.time()}
# ---
tab = {
    "delta": 0,
    "done": 0,
    "file_date": "",
    "len_all_props": 0,
    "items_0_claims": 0,
    "items_1_claims": 0,
    "items_no_P31": 0,
    "All_items": 0,
    "total_claims": 0,
    "properties": {},
    "langs": {},
}

time_start = time.time()


def print_memory():
    yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    end = time.time()
    delta = int(end - time_start)
    print(yellow % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")


def log_dump(tab):
    # ---
    jsonname = Path(__file__).parent / "claims.json"
    # ---
    with open(jsonname, "w", encoding="utf-8") as outfile:
        ujson.dump(tab, outfile)
    # ---
    print("log_dump done")


def do_line(json1):
    tab["All_items"] += 1
    tab["done"] += 1

    claims = json1.get("claims", {})

    # Instead of repeatedly checking length, calculate it once
    claims_length = len(claims)

    if claims_length == 0:
        tab["items_0_claims"] += 1
    elif claims_length == 1:
        tab["items_1_claims"] += 1

    if "P31" not in claims:
        tab["items_no_P31"] += 1

    _json1 = {
        "qid": "Q31",
        "labels": ["el", "ay"],
        "aliases": ["cy", "sk", "mk", "vls"],
        "descriptions": ["cy", "sk", "mk", "vls"],
        "sitelinks": ["itwikivoyage", "zhwikivoyage", "ruwikivoyage", "fawikiquote", "dewikivoyage"],
        "claims": {"P1344": ["Q1088364"], "P31": ["Q3624078", "Q43702", "Q6256", "Q20181813", "Q185441", "Q1250464", "Q113489728"]},
    }

    for p, p_qids in claims.items():
        tab["total_claims"] += len(p_qids)

        p_tab = tab["properties"].get(p)

        if not p_tab:
            p_tab = {
                "qids": {"others": 0},
                "lenth_of_usage": 0,
                "len_prop_claims": 0,
            }

        p_tab["lenth_of_usage"] += 1
        p_tab["len_prop_claims"] += len(p_qids)

        for qid in p_qids:
            if qid:
                p_tab["qids"][qid] = p_tab["qids"].get(qid, 0) + 1

        tab["properties"][p] = p_tab


def get_lines(jsonfiles):
    for items_file in tqdm.tqdm(jsonfiles):
        with open(items_file, "r", encoding="utf-8") as f:
            for line in ujson.load(f):
                yield line


def read_file():
    # ---
    # read all json files in parts_dir
    jsonfiles = [x for x in parts_dir.glob("*.json")]
    print(f"all json files: {len(jsonfiles)}")
    files = get_lines(jsonfiles)
    # ---
    cc = 0
    # ---
    for cc, line in tqdm.tqdm(enumerate(files, start=1)):
        # ---
        do_line(line)
        # ---
        if cc % 100000 == 0:
            print(cc, time.time() - tt[1])
            tt[1] = time.time()
            print_memory()
    # ---
    print(f"all_items: {cc}")
    # ---
    print(f"read all lines: {tab['done']}")
    # ---
    for x, xx in tab["properties"].items():
        tab["properties"][x]["len_of_qids"] = len(xx["qids"])
        # sort xx["qids"] by value
        qids_1 = sorted(xx["qids"].items(), key=lambda x: x[1], reverse=True)
        # get only first 100
        tab["properties"][x]["qids"] = dict(qids_1[:100])
        tab["properties"][x]["qids"]["others"] = xx["qids"].get("others", 0)
    # ---
    tab["len_all_props"] = len(tab["properties"])
    # ---
    end = time.time()
    delta = int(end - time_start)
    print(f"read_file: done in {delta}")
    # ---
    tab["delta"] = f"{delta:,}"
    # ---
    log_dump(tab)


if __name__ == "__main__":
    read_file()
