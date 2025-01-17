"""
python3 core8/pwb.py dump3/read_json test nodump
python3 /data/project/himo/bots/dump_core/dump3/read_json.py test

https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2
https://dumps.wikimedia.org/wikidatawiki/entities/latest-truthy.nt.bz2

"""

import psutil
import os
import ujson
import sys
import time
from datetime import datetime
from pathlib import Path
from qwikidata.json_dump import WikidataJsonDump

# ---
bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
# bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-truthy.nt.bz2"
# ---
va_dir = Path(__file__).parent
# ---
done_lines = va_dir / "done_lines.txt"

with open(done_lines, "w", encoding="utf-8") as f:
    f.write("")

do_test = "test" in sys.argv
# ---
items_file = va_dir / "jsons/items.json"
# ---
if do_test:
    items_file = va_dir / "jsons/items_test.json"
# ---
with open(items_file, "w", encoding="utf-8") as f:
    f.write("")

tab = {
    "delta": 0,
    "done": 0,
    "file_date": "",
    "len_all_props": 0,
    "items_0_claims": 0,
    "items_1_claims": 0,
    "items_no_P31": 0,
    "All_items": 0,
    "all_claims_2020": 0,
    "properties": {},
    "langs": {},
}

from rdflib import Graph


def read_nt_dump(file_path):
    g = Graph()
    g.parse(file_path, format="nt")
    return g


def print_memory():
    yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    print(yellow % "Memory usage:", purple % f"{usage} MB")


def get_most_props():
    # ---
    properties_path = va_dir / "properties.json"
    with open(properties_path, "r", encoding="utf-8") as f:
        data = ujson.load(f)
    # ---
    return data


most_props = get_most_props()


def dump_it(tab):
    if "nodump" in sys.argv:
        return
    # ---
    with open(items_file, "w", encoding="utf-8") as outfile:
        ujson.dump(tab, outfile)
    # ---
    print(f"log_dump done to file: {items_file}")


def do_line(entity_dict):
    tab["done"] += 1

    # Avoid repeated calculations
    if "pp" in sys.argv:
        print(entity_dict)

    json1 = entity_dict

    # entity_dict.keys = ['type', 'id', 'labels', 'descriptions', 'aliases', 'claims', 'sitelinks', 'pageid', 'ns', 'title', 'lastrevid', 'modified']

    claims = json1.get("claims", {})

    # Instead of repeatedly checking length, calculate it once
    claims_length = len(claims)

    if claims_length == 0:
        tab["items_0_claims"] += 1
    elif claims_length == 1:
        tab["items_1_claims"] += 1

    _claims_example = {
        "claims": {"P31": [{"mainsnak": {"snaktype": "value", "property": "P31", "hash": "b44ad788a05b4c1b2915ce0292541c6bdb27d43a", "datavalue": {"value": {"entity-type": "item", "numeric-id": 6256, "id": "Q6256"}, "type": "wikibase-entityid"}, "datatype": "wikibase-item"}, "type": "statement", "id": "Q805$81609644-2962-427A-BE11-08BC47E34C44", "rank": "normal"}]},
    }

    if "P31" not in claims:
        tab["items_no_P31"] += 1

    # json1 = {"qid": "Q31", "labels": ["el", "ay"], "descriptions": ["cy", "sk", "mk", "vls"], "sitelinks": ["itwikivoyage", "zhwikivoyage", "ruwikivoyage", "fawikiquote", "dewikivoyage"], "claims": {"P1344": ["Q1088364"], "P31": ["Q3624078", "Q43702", "Q6256", "Q20181813", "Q185441", "Q1250464", "Q113489728"]}}

    for p, p_qids in claims.items():
        Type = p_qids[0].get("mainsnak", {}).get("datatype", "")
        tab["all_claims_2020"] += len(p_qids)

        if p not in most_props:
            continue

        if Type == "wikibase-item":
            properties_p = tab["properties"].get(p)
            if not properties_p:
                properties_p = {
                    "qids": {"others": 0},
                    "lenth_of_usage": 0,
                    "len_prop_claims": 0,
                }
                tab["properties"][p] = properties_p

            properties_p["lenth_of_usage"] += 1
            properties_p["len_prop_claims"] += len(p_qids)

            for claim in p_qids:
                datavalue = claim.get("mainsnak", {}).get("datavalue", {})
                idd = datavalue.get("value", {}).get("id")

                del datavalue

                if idd:
                    properties_p_qids = properties_p["qids"]
                    properties_p_qids[idd] = properties_p_qids.get(idd, 0) + 1

                del idd

    # ---

    tats = ["labels", "descriptions", "aliases"]
    for x in tats:
        for code in json1.get(x, {}):
            if code not in tab["langs"]:
                tab["langs"][code] = {"labels": 0, "descriptions": 0, "aliases": 0}
            tab["langs"][code][x] += 1

    del json1
    del claims


def get_file_info(file_path):
    # Get the time of last modification
    last_modified_time = os.path.getmtime(file_path)

    return datetime.fromtimestamp(last_modified_time).strftime("%Y-%m-%d")


def check_file_date(file_date):
    file = va_dir / "file_date.txt"
    if not file.exists():
        return
    # ---
    old_date = file.read_text(encoding="utf-8")
    # ---
    print(f"file_date: {file_date}, old_date: {old_date}")
    # ---
    if old_date == file_date and "test" not in sys.argv and "test1" not in sys.argv:
        print(f"file_date: {file_date} <<lightred>> unchanged")
        sys.exit(0)


def read_lines(tst_limit, bz2_file):
    print("def read_lines():")
    # ---
    for p, _ in most_props.items():
        tab["properties"][p] = {
            "qids": {"others": 0},
            "lenth_of_usage": 0,
            "len_prop_claims": 0,
        }
    # ---
    tt = time.time()
    # ---
    wjd = WikidataJsonDump(bz2_file)
    # ---
    numbs = 5000 if do_test else 100000
    dump_numbs = 10000 if do_test else 1000000
    # ----
    for cc, entity_dict in enumerate(wjd):
        # ---
        if entity_dict["type"] == "item":
            tab["All_items"] += 1
            # ---
            do_line(entity_dict)
            # ---
            if cc % numbs == 0:
                print("cc:", cc, time.time() - tt)
                tt = time.time()
                print_memory()
            # ---
            if cc % dump_numbs == 0:
                dump_it(tab)
                # ---
                print(f"{cc=}")
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
    dump_it(tab)


def main():
    time_start = time.time()
    # ---
    print(f"time_start:{str(time_start)}")
    # ---
    test_limit = 50000  # if "-limit" in sys.argv else None
    # ---
    for arg in sys.argv:
        arg, _, value = arg.partition(":")
        if arg == "-limit":
            test_limit = int(value)
    # ---
    print(f"read_file: read file: {bz2_file}")

    if not os.path.isfile(bz2_file):
        print(f"file {bz2_file} <<lightred>> not found")
        return {}

    tab["file_date"] = get_file_info(bz2_file)
    print(f"file date: {tab['file_date']}")

    print(f"file {bz2_file} found, read it:")
    # ---
    check_file_date(tab["file_date"])
    # ---
    read_lines(test_limit, bz2_file)
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
    if "test" not in sys.argv and "nodump" not in sys.argv:
        with open(f"{va_dir}/file_date.txt", "w", encoding="utf-8") as outfile:
            outfile.write(tab["file_date"])


if __name__ == "__main__":
    main()
