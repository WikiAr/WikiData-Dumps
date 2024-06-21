"""
python3 /data/project/himo/bots/dump_core/dump2/read_d.py one
python3 /data/project/himo/bots/dump_core/dump2/read_d.py test
tfj run dump2 --mem 1Gi --image python3.9 --command "$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/read_d.py"


"""
import os
import psutil
import json
import sys
import time
from pathlib import Path
from qwikidata.json_dump import WikidataJsonDump
# ---

time_start = time.time()
print(f"time_start:{str(time_start)}")
# ---
bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
# ---
done_lines = "/data/project/himo/bots/dump_core/dump2/done_lines.txt"

with open(done_lines, "w", encoding="utf-8") as f:
    f.write("")


def get_most_props():
    # ---
    properties_path = Path(__file__).parent / "properties.json"
    with open(properties_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # ---
    return data


most_props = get_most_props()


def print_memory():
    yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    print(yellow % "Memory usage:", purple % f"{usage} MB")


def dump_lines(lines, items_file):
    if not lines:
        return
    text = "\n".join([json.dumps(line) for line in lines])
    with open(items_file, "a", encoding="utf-8") as f:
        f.write(f"{text}\n")


def fix_property(pv):
    return [claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id") for claim in pv]


def do_line(json1):
    # json1.keys = ['type', 'id', 'labels', 'descriptions', 'aliases', 'claims', 'sitelinks', 'pageid', 'ns', 'title', 'lastrevid', 'modified']

    claims = json1.get("claims", {})
    qid_text = {
        "qid": json1["title"],
        "labels": list(json1.get("labels", {}).keys()),
        "descriptions": list(json1.get("descriptions", {}).keys()),
        "aliases": list(json1.get("aliases", {}).keys()),
        "sitelinks": list(json1.get("sitelinks", {}).keys()),
        # "claims": {p: fix_property(pv) for p, pv in claims.items() if p in most_props}
    }

    qid_text["claims"] = {
        p: fix_property(pv)
        for p, pv in claims.items()
        if p in most_props
        and pv[0].get("mainsnak", {}).get("datatype", "") == "wikibase-item"
    }

    del claims

    return qid_text


def read_lines(do_test, tst_limit, bz2_file, items_file):
    print("def read_lines():")
    # ---
    tt = time.time()
    # ---
    wjd = WikidataJsonDump(bz2_file)
    # ---
    lines = []
    # ---
    numbs = 5000 if do_test else 100000
    dump_numbs = 10000 if do_test else 1000000
    # ----
    for cc, entity_dict in enumerate(wjd):
        # ---
        if entity_dict["type"] == "item":
            # ---
            line = do_line(entity_dict)
            lines.append(line)
            # ---
            if cc % dump_numbs == 0:
                dump_lines(lines, items_file)
                # ---
                del lines
                # ---
                lines = []
                print(f"dump_lines:{cc}, len lines:{len(lines)}")
            # ---
            if cc % numbs == 0:
                print("cc:", cc, time.time() - tt)
                tt = time.time()
                print_memory()
            # ---
            if do_test and cc > tst_limit:
                print("cc>tst_limit")
                break
            # ---
            if cc % 1000000 == 0:
                with open(done_lines, "a", encoding="utf-8") as f:
                    f.write(f"done: {cc:,}\n")
        # ---
        del entity_dict
    # ---
    dump_lines(lines, items_file)


def main():
    time_start = time.time()
    # ---
    do_test = "test" in sys.argv
    # ---
    items_file = "/data/project/himo/bots/dump_core/dump2/jsons/items.json"
    # ---
    if do_test:
        items_file = "/data/project/himo/bots/dump_core/dump2/jsons/items_test.json"
    # ---
    with open(items_file, "w", encoding="utf-8") as f:
        f.write("")
    # ---
    test_limit = 50000  # if "-limit" in sys.argv else None
    # ---
    for arg in sys.argv:
        arg, _, value = arg.partition(":")
        if arg == "-limit":
            test_limit = int(value)
    # ---
    read_lines(do_test, test_limit, bz2_file, items_file)
    # ---
    end = time.time()
    delta = int(end - time_start)
    print(f"read_file: done in {delta}")


if __name__ == "__main__":
    main()
