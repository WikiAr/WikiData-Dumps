import os
import tqdm
import ujson
from pathlib import Path
import gc
import sys
from humanize import naturalsize
import time
import psutil

Dir = Path(__file__).parent.parent / "parts_claims"

jsons_files = list(Dir.glob("*.json"))
print(f"length of jsons_files: {len(jsons_files)}")
jsons_files.sort()
tt = {1: time.time()}
start_time = time.time()


def print_memory(cc):
    print(cc, time.time() - tt[1])
    tt[1] = time.time()

    green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"
    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = naturalsize(usage, binary=True)
    delta = int(time.time() - start_time)

    print(green % "Memory usage:", purple % f"{usage}", f"time: to now {delta}")


tab = {
    "delta": 0,
    "done": 0,
    "file_date": "",
    "total_properties_count": 0,
    "items_with_0_claims": 0,
    "items_with_1_claim": 0,
    "items_missing_P31": 0,
    "All_items": 0,
    "total_claims_count": 0,
    "properties": {},
}

n = 0

with open(jsons_files[0], "r", encoding="utf-8") as f:
    print(f"file: {jsons_files[0]}")
    tab = ujson.load(f)
    n = 1
# ----
for x in tqdm.tqdm(jsons_files[1:]):
    n += 1
    # ---
    print(f"file: {x}")
    # ---
    with open(x, "r", encoding="utf-8") as f:
        data = ujson.load(f)
    # ----
    for x, v in data.items():
        if isinstance(v, int):
            tab[x] += v
    # ---
    print(f"len(properties): {len(data['properties'])}")
    # ---
    if "no" in sys.argv:
        continue
    # ---
    # Process properties in chunks to reduce memory usage
    CHUNK_SIZE = 1000
    property_items = list(data["properties"].items())

    for i in range(0, len(property_items), CHUNK_SIZE):
        chunk = property_items[i : i + CHUNK_SIZE]
        for p, stab in tqdm.tqdm(chunk, leave=False):
            if p not in tab["properties"]:
                tab["properties"][p] = stab
            else:
                tab["properties"][p]["property_claims_count"] += stab["property_claims_count"]
                tab["properties"][p]["lenth_of_usage"] += stab["lenth_of_usage"]
            # ---
            for x, count in stab["qids"].items():
                tab["properties"][p]["qids"].setdefault(x, 0)
                tab["properties"][p]["qids"][x] += count
        gc.collect()  # More frequent garbage collection
    # ---
    gc.collect()
    # ---
    print_memory(n)

with open(Dir / "claims_tabs.json", "w", encoding="utf-8") as f:
    ujson.dump(tab, f)
