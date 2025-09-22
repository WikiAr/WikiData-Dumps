"""
https://hub-paws.wmcloud.org/user/Mr.%20Ibrahem/lab/tree/dump

python3 /data/project/himo/bots/dump_core/dump25/r_27.py

tfj run dump2 --mem 1Gi --image python3.9 --command "$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump25/r_27.py"

current_count: 150000 time: 34.07094955444336
current_count: 162500 time: 32.720284938812256

"""
import os
import psutil
import gc
import json
import time
import bz2
from pathlib import Path
from humanize import naturalsize  # naturalsize(file_size, binary=True)

time_start = time.time()


def check_dir(path):
    if not path.exists():
        path.mkdir()


done1_lines = Path(__file__).parent / "r_claims_lines.txt"

with open(done1_lines, "w", encoding="utf-8") as f:
    f.write("")

tt = {1: 0}

properties_path = Path(__file__).parent / "properties.json"

with open(properties_path, "r", encoding="utf-8") as f:
    most_props = json.load(f)


tabs = {
    "total_properties_count": 0,
    "items_with_0_claims": 0,
    "items_with_1_claim": 0,
    "items_missing_P31": 0,
    "All_items": 0,
    "total_claims_count": 0,
    "properties": {},
}


def dump_lines_claims(linesc):
    # ---
    if not linesc:
        return
    # ---
    tabs["All_items"] += len(linesc)
    # ---
    for line in linesc:
        # ---
        claims = line.get("claims", {})
        # ---
        claims_length = len(claims)
        # ---
        if claims_length == 0:
            tabs["items_with_0_claims"] += 1
            continue

        if claims_length == 1:
            tabs["items_with_1_claim"] += 1

        if "P31" not in claims:
            tabs["items_missing_P31"] += 1

        # ---
        for pid, len_qids in claims.items():
            # ---
            tabs["total_claims_count"] += len_qids
            # ---
            if pid not in tabs["properties"]:
                tabs["properties"][pid] = {
                    "items_with_property": 0,
                    "lenth_of_usage": 0,
                    "unique_qids_count": 0,
                    "property_claims_count": 0,
                }
            # ---
            tabs["properties"][pid]["property_claims_count"] += len_qids
            tabs["properties"][pid]["lenth_of_usage"] += 1
            tabs["properties"][pid]["items_with_property"] += 1
        # ---
        del claims, line
    # ---


def print_memory(i):
    now = time.time()

    print("current_count:", i, "time:", now - tt[1])
    tt[1] = now
    # ---
    green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    delta = int(now - time_start)
    print(green % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")


def parse_lines(bz2_file):
    with bz2.open(bz2_file, "r") as f:
        for line in f:
            line = line.decode("utf-8").strip("\n").strip(",")
            if line.startswith("{") and line.endswith("}"):
                yield line


def filter_and_process(entity_dict):
    entity_dict = json.loads(entity_dict)
    if entity_dict["type"] == "item":
        claims = entity_dict.get("claims", {})
        line2 = {
            "qid": entity_dict["title"],
            "claims": {p: len(pv) for p, pv in claims.items() if p in most_props},
        }
        return line2
    return None


def process_file(bz2_file):
    tt[1] = time.time()
    mem_nu = 10000
    dump_numbs = 100000
    # ---
    lines_claims = []
    # ---
    # for i, entity_dict in tqdm.tqdm(enumerate(parse_lines(), start=1)):
    for i, entity_dict in enumerate(parse_lines(bz2_file), start=1):

        line2 = filter_and_process(entity_dict)
        if line2:
            lines_claims.append(line2)

        if dump_numbs == len(lines_claims):
            print(f"dump_lines_claims:{i}, len lines_claims:{len(lines_claims)}")
            # ---
            dump_lines_claims(lines_claims)
            # ---
            lines_claims.clear()
            gc.collect()
            # ---
            ti = time.time() - tt[1]
            # ---
            print_memory(i)
            # ---
            with open(done1_lines, "a", encoding="utf-8") as f:
                f.write(f"done: {i:,} {ti}\n")
            # ---
        elif i % mem_nu == 0:
            print_memory(i)

    # ---
    if lines_claims:
        dump_lines_claims(lines_claims)

    items_file_fixed = Path(__file__).parent / "r_claims.json"
    # ---
    with open(items_file_fixed, "w", encoding="utf-8") as f:
        json.dump(tabs, f)
    # ---
    items_file_fixed_size = naturalsize(os.path.getsize(items_file_fixed), binary=True)
    # ---
    print(f"dump_lines_claims fixed: {items_file_fixed_size}")

    print("Processing completed.")


def main():
    bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"

    file_size = os.path.getsize(bz2_file)

    print(naturalsize(file_size, binary=True))

    process_file(bz2_file)

    end = time.time()
    delta = int(end - time_start)
    print(f"read_file: done in {delta}")


if __name__ == "__main__":
    main()
