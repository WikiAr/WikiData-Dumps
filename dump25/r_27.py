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
import sys
import tqdm
import bz2
from pathlib import Path
from humanize import naturalsize

# ---
Dir = Path(__file__).parent
# ---
dump_dir = Dir / "parts"
# ---
if not dump_dir.exists():
    dump_dir.mkdir()
# ---
dump_done = {1: 0}

done_lines = Dir / "done_lines.txt"

with open(done_lines, "w", encoding="utf-8") as f:
    f.write("")

tt = {1: 0}


def dump_lines(lines):
    if not lines:
        return
    # ---
    dump_done[1] += 1
    # ---
    items_file = dump_dir / f"items_{dump_done[1]}.json"
    # ---
    with open(items_file, "w", encoding="utf-8") as f:
        json.dump(lines, f)


def print_memory(i):
    now = time.time()

    print("current_count:", i, "time:", now - tt[1])
    tt[1] = now
    # ---
    yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    delta = int(now - time_start)
    print(yellow % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")


def fix_property(pv):
    return [claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id") for claim in pv]


properties_path = Path(__file__).parent / "properties.json"
# ---
with open(properties_path, "r", encoding="utf-8") as f:
    most_props = json.load(f)
# ---
bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"

file_size = os.path.getsize(bz2_file)

print(naturalsize(file_size, binary=True))


def parse_lines():
    with bz2.open(bz2_file, "r") as f:
        for line in f:
            line = line.decode("utf-8").strip("\n").strip(",")
            if line.startswith("{") and line.endswith("}"):
                yield line


def filter_and_process(entity_dict):
    entity_dict = json.loads(entity_dict)
    if entity_dict["type"] == "item":
        claims = entity_dict.get("claims", {})
        line = {
            "qid": entity_dict["title"],
            "labels": list(entity_dict.get("labels", {}).keys()),
            "descriptions": list(entity_dict.get("descriptions", {}).keys()),
            "aliases": list(entity_dict.get("aliases", {}).keys()),
            "sitelinks": list(entity_dict.get("sitelinks", {}).keys()),
            "claims": {p: fix_property(pv) for p, pv in claims.items() if p in most_props and pv[0].get("mainsnak", {}).get("datatype", "") == "wikibase-item"},
        }
        return line
    return None


time_start = time.time()


def process_file():
    tt[1] = time.time()
    mem_nu = 12500
    dump_numbs = 25000
    # ---
    skip_to = 0
    # ---
    if "skip" in sys.argv:
        js_f = [int(x.name.replace(".json", "").replace("items_", "")) for x in dump_dir.glob("*.json")]
        maxfile = max(js_f) if js_f else 0
        skip_to = maxfile * dump_numbs
        dump_done[1] = maxfile
        print("skip_to:", skip_to, "max file:", maxfile)
    # ---
    print_frist = True
    # ---
    lines = []
    # for i, entity_dict in tqdm.tqdm(enumerate(parse_lines(), start=1)):
    for i, entity_dict in enumerate(parse_lines(), start=1):
        if i < skip_to:
            if i % dump_numbs == 0:
                print("skip_to:", skip_to, "i:", i)
                # print_memory(i)
            continue

        if print_frist:
            print_memory(i)
            print_frist = False
            print("print_frist = False")

        line = filter_and_process(entity_dict)
        if line:
            lines.append(line)

        if dump_numbs == len(lines):
            # if i % dump_numbs == 0:
            print(f"dump_lines:{i}, len lines:{len(lines)}")
            # ---
            dump_lines(lines)
            # ---
            lines.clear()
            gc.collect()
            # ---
            ti = time.time() - tt[1]
            # ---
            print_memory(i)
            # ---
            with open(done_lines, "a", encoding="utf-8") as f:
                f.write(f"done: {i:,} {ti}\n")
        elif i % mem_nu == 0:
            print_memory(i)

    if lines:
        dump_lines(lines)

    print("Processing completed.")


process_file()

end = time.time()
delta = int(end - time_start)
print(f"read_file: done in {delta}")
