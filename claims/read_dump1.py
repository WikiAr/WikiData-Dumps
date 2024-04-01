
import os
import ujson as json
import sys
import bz2
import time
from datetime import datetime
from pathlib import Path
time_start = time.perf_counter()

va_dir = Path(__file__).parent
filename = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
Dump_Dir = "/data/project/himo/dumps"

jsonname = f"{Dump_Dir}/claims.json"
tt = {1: time.perf_counter()}
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
def log_dump(tab):
    if "nodump" in sys.argv:
        return
    with open(jsonname, "w", encoding="utf-8") as outfile:
        json.dump(tab, outfile)
    print("log_dump done")
def do_line(line):
    tab["done"] += 1
    json1 = json.loads(line)
    claims = json1.get("claims", {})

    claims_length = len(claims)
    if claims_length == 0:
        tab["items_0_claims"] += 1
    elif claims_length == 1:
        tab["items_1_claims"] += 1
    if "P31" not in claims:
        tab["items_no_P31"] += 1
    for p in claims.keys():
        Type = claims[p][0].get("mainsnak", {}).get("datatype", "")
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
            tab["all_claims_2020"] += len(claims[p])
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
    if old_date == file_date:
        print(f"file_date: {file_date} <<lightred>> unchanged")
        sys.exit(0)
def read_lines():
    cc = 0
    with bz2.open(filename, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n,")
            if line.startswith("{") and line.endswith("}"):
                tab["All_items"] += 1
                cc += 1
                do_line(line)
                if cc % 1000000 == 0:
                    log_dump(tab)
def read_file():
    if not os.path.isfile(filename):
        return {}
    tab["file_date"] = get_file_info(filename)
    check_file_date(tab["file_date"])
    read_lines()
    for x, xx in tab["properties"].items():
        tab["properties"][x]["len_of_qids"] = len(xx["qids"])
    tab["len_all_props"] = len(tab["properties"])
    end = time.perf_counter()
    delta = int(end - time_start)
    tab["delta"] = f"{delta:,}"
    log_dump(tab)
    if "nodump" not in sys.argv:
        with open(f"{va_dir}/file_date.txt", "w", encoding="utf-8") as outfile:
            outfile.write(tab["file_date"])
if __name__ == "__main__":
    read_file()