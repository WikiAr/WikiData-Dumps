"""
from dump.claims.read_dump import read_file
python3 core8/pwb.py dump/claims/read_dump test nodump
python3 /data/project/himo/bots/dump_core/dump/claims/read_dump.py test

https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2

"""
import os

# import json
import ujson as json
import sys
import bz2
import time
from datetime import datetime
from pathlib import Path
from qwikidata.json_dump import WikidataJsonDump
# ---
time_start = time.perf_counter()
print(f"time_start:{str(time_start)}")
# ---
# split after /dump
core_dir = str(Path(__file__)).replace("\\", "/").split("/dump/", maxsplit=1)[0]
print(f"core_dir:{core_dir}")
sys.path.append(core_dir)
print(f"sys.path.append:core_dir: {core_dir}")
# ---
from dump.memory import print_memory

va_dir = Path(__file__).parent
# ---
properties_path = va_dir / "properties.json"
# ---
# from dump.claims.fix_dump import fix_props
# ---
filename = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
# ---
Dump_Dir = "/data/project/himo/bots/dumps"
# ---
if os.path.exists(r"I:\core\dumps"):
    Dump_Dir = r"I:\core\dumps"
# ---
print(f"Dump_Dir:{Dump_Dir}")
# ---
test_limit = {1: 50000}
# ---
for arg in sys.argv:
    arg, _, value = arg.partition(":")
    if arg == "-limit":
        test_limit[1] = int(value)
# ---
jsonname = f"{Dump_Dir}/claims.json"

if "test" in sys.argv:
    jsonname = f"{Dump_Dir}/claims_test.json"

tt = {1: time.perf_counter()}
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
    "all_claims_2020": 0,
    "properties": {},
    "langs": {},
}

def get_most_props():
    # ---
    with open(properties_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # ---
    return data
    
most_props = get_most_props()

def log_dump(tab):
    if "nodump" in sys.argv:
        return
    # ---
    with open(jsonname, "w", encoding="utf-8") as outfile:
        json.dump(tab, outfile)
    # ---
    print("log_dump done")


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

    claims_example = {"claims": {"P31": [{"mainsnak": {"snaktype": "value", "property": "P31", "hash": "b44ad788a05b4c1b2915ce0292541c6bdb27d43a", "datavalue": {"value": {"entity-type": "item", "numeric-id": 6256, "id": "Q6256"}, "type": "wikibase-entityid"}, "datatype": "wikibase-item"}, "type": "statement", "id": "Q805$81609644-2962-427A-BE11-08BC47E34C44", "rank": "normal"}]}}

    if "P31" not in claims:
        tab["items_no_P31"] += 1

    for p in claims.keys():
        Type = claims[p][0].get("mainsnak", {}).get("datatype", "")
        tab["all_claims_2020"] += len(claims[p])

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
            properties_p["len_prop_claims"] += len(claims[p])

            for claim in claims[p]:
                datavalue = claim.get("mainsnak", {}).get("datavalue", {})
                idd = datavalue.get("value", {}).get("id")

                del datavalue

                if idd:
                    properties_p_qids = properties_p["qids"]
                    properties_p_qids[idd] = properties_p_qids.get(idd, 0) + 1

                del idd

    del json1
    del claims


def get_file_info(file_path):
    # Get the time of last modification
    last_modified_time = os.path.getmtime(file_path)

    return datetime.fromtimestamp(last_modified_time).strftime("%Y-%m-%d")


def check_file_date(file_date):
    with open(f"{va_dir}/file_date.txt", "r", encoding="utf-8") as outfile:
        old_date = outfile.read()
    # ---
    print(f"file_date: {file_date}, old_date: {old_date}")
    # ---
    if old_date == file_date and "test" not in sys.argv and "test1" not in sys.argv:
        print(f"file_date: {file_date} <<lightred>> unchanged")
        sys.exit(0)


def read_lines():
    print("def read_lines():")
    # ---
    wjd = WikidataJsonDump(filename)
    # ---
    for cc, entity_dict in enumerate(wjd):
        # ---
        if entity_dict["type"] == "item":
            tab["All_items"] += 1
            # ---
            do_line(entity_dict)
            # ---
            if cc % 100000 == 0:
                print(cc, time.perf_counter() - tt[1])
                tt[1] = time.perf_counter()
                # print memory usage
                print_memory()
            # ---
            if cc % 1000000 == 0:
                log_dump(tab)


def read_lines_test():
    print("def read_lines_test():")
    # ---
    wjd = WikidataJsonDump(filename)
    # ---
    for cc, entity_dict in enumerate(wjd):
        # ---
        if entity_dict["type"] == "item":
            tab["All_items"] += 1
            # ---
            do_line(entity_dict)
            # ---
            if cc % 100 == 0:
                print(f"cc:{cc}")
                print(f"done:{tab['done']}")
                # ---
                print(cc, time.perf_counter() - tt[1])
                tt[1] = time.perf_counter()
                # print memory usage
                print_memory()
            # ---
            if cc > test_limit[1]:
                print("cc>test_limit[1]")
                break


def read_file():
    # ---
    for p,_ in most_props.items():
        tab["properties"][p] = {
                "qids": {"others": 0},
                "lenth_of_usage": 0,
                "len_prop_claims": 0,
        }
    # ---
    print(f"read_file: read file: {filename}")

    if not os.path.isfile(filename):
        print(f"file {filename} <<lightred>> not found")
        return {}

    tab["file_date"] = get_file_info(filename)
    print(f"file date: {tab['file_date']}")

    print(f"file {filename} found, read it:")
    # ---
    check_file_date(tab["file_date"])
    # ---
    if "test" in sys.argv:
        read_lines_test()
    else:
        read_lines()
    # ---
    print(f"read all lines: {tab['done']}")
    # ---
    for x, xx in tab["properties"].items():
        tab["properties"][x]["len_of_qids"] = len(xx["qids"])
    # ---
    tab["len_all_props"] = len(tab["properties"])
    # ---
    end = time.perf_counter()
    # ---
    delta = int(end - time_start)
    tab["delta"] = f"{delta:,}"
    # ---
    print(f"read_file: done in {tab['delta']}")
    # ---
    log_dump(tab)
    # ---
    if "test" not in sys.argv and "nodump" not in sys.argv:
        with open(f"{va_dir}/file_date.txt", "w", encoding="utf-8") as outfile:
            outfile.write(tab["file_date"])


if __name__ == "__main__":
    read_file()
