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
import ujson
import time
import sys

# import tqdm
import bz2
import requests
from pathlib import Path
from humanize import naturalsize  # naturalsize(file_size, binary=True)
sys.path.append(str(Path(__file__).parent))

from dir_handler import split_by_pid_dir, dump_dir_claims_fixed, dump_parts1_fixed, dump_files_dir

time_start = time.time()

dump_done = {1: 0, "claims": 0}

done1_lines = dump_files_dir / "done1_lines.txt"

with open(done1_lines, "w", encoding="utf-8") as f:
    f.write("")

tt = {1: 0}

most_path = dump_files_dir / "most_claims.json"

if not most_path.exists():
    most_path.write_text('{"q": "", "count": 0}')

most_data = json.loads(most_path.read_text())


def dump_lines_claims(linesc):
    global most_data
    # ---
    if not linesc:
        return {}
    # ---
    dump_done["claims"] += 1
    # ---
    # items_file = dump_dir_claims / f"{dump_done['claims']}.json"
    # ---
    # with open(items_file, "w", encoding="utf-8") as f: json.dump(linesc, f)
    # ---
    _line = {
        "qid": "Q00",
        "claims": {"P31": ["Q5", "Q0"]},
    }
    # ---
    most = {"q": "", "count": 0}
    # ---
    tabs_properties = {}
    tabs = {
        "len_all_props": 0,
        "items_0_claims": 0,
        "items_1_claims": 0,
        "items_no_P31": 0,
        "All_items": 0,
        "total_claims": 0,
        "properties": {},
    }
    # ---
    tabs["All_items"] += len(linesc)
    # ---
    for line in linesc:
        # ---
        claims = line.get("claims", {})
        # ---
        _claims = {"P59": ["Q10519"], "P31": ["Q523", "Q67206691"], "P6259": ["Q1264450"]}
        # ---
        claims_length = len(claims)
        # ---
        if claims_length > most["count"]:
            most["count"] = claims_length
            most["q"] = line["qid"]
        # ---
        if claims_length == 0:
            tabs["items_0_claims"] += 1
            continue

        if claims_length == 1:
            tabs["items_1_claims"] += 1

        if "P31" not in claims:
            tabs["items_no_P31"] += 1
        # ---
        for pid, qids in claims.items():
            # ---
            tabs["total_claims"] += len(qids)
            # ---
            if pid not in tabs_properties:
                tabs_properties[pid] = {
                    "qids": {},
                    "items_use_it": 0,
                    "len_of_usage": 0,
                    # "len_of_qids": 0,
                    "len_prop_claims": 0,
                }
            # ---
            tabs_properties[pid]["len_prop_claims"] += len(qids)
            tabs_properties[pid]["len_of_usage"] += 1
            tabs_properties[pid]["items_use_it"] += 1
            # ---
            for qid in qids:
                if qid not in tabs_properties[pid]["qids"]:
                    tabs_properties[pid]["qids"][qid] = 0
                # ---
                tabs_properties[pid]["qids"][qid] += 1
        # ---
        del claims, line
    # ---
    if most["count"] > most_data["count"]:
        most_path.write_text(json.dumps(most))
        # ---
        most_data = most
    # ---
    items_file_fixed = dump_dir_claims_fixed / f"{dump_done['claims']}.json"
    # ---
    tabs["properties"] = tabs_properties
    # ---
    # with open(items_file_fixed, "w", encoding="utf-8") as f: json.dump(tabs, f)
    # ---
    for pid, data in tabs_properties.items():
        # ---
        data["pid"] = pid
        # ---
        pid_file = split_by_pid_dir / f"{pid}.json"
        # ---
        if not pid_file.exists():
            pid_file.touch()
        # ---
        with open(pid_file, "a", encoding="utf-8") as outfile:
            outfile.write(ujson.dumps(data) + "\n")
    # ---
    # items_file_size = naturalsize(os.path.getsize(items_file), binary=True)
    # print(f"dump_lines claims size: {items_file_size}, fixed: {items_file_fixed_size}")
    # ---
    items_file_fixed_size = naturalsize(os.path.getsize(items_file_fixed), binary=True)
    # ---
    print(f"dump_lines claims fixed: {items_file_fixed_size}")

    # ---------- NEW: return statistics used by the caller ----------
    return tabs


def dump_lines(lines):
    if not lines:
        return
    # ---
    dump_done[1] += 1
    # ---
    # items_file = dump_dir / f"{dump_done[1]}.json"
    # ---
    # with open(items_file, "w", encoding="utf-8") as f: json.dump(lines, f)
    # ---
    tab = {
        "no": {
            "labels": 0,
            "descriptions": 0,
            "aliases": 0,
            "sitelinks": 0,
        },
        "most": {
            "labels": {"q": "", "count": 0},
            "descriptions": {"q": "", "count": 0},
            "aliases": {"q": "", "count": 0},
            "sitelinks": {"q": "", "count": 0},
        },
        "All_items": 0,
        "sitelinks": {},
        "langs": {},
    }
    # ---
    tab["All_items"] += len(lines)
    # ---
    _json1 = {
        "labels": ["el", "ay"],
        "aliases": ["el", "ay"],
        "descriptions": ["cy", "sk", "mk", "vls"],
        "sitelinks": ["arwiki", "enwiki", "mk", "vls"],
    }
    # ---
    tats = ["labels", "descriptions", "aliases", "sitelinks"]
    # ---
    for json1 in lines:
        for x in tats:
            # ---
            ta_o = json1.get(x, {})
            # ---
            if len(ta_o) == 0:
                tab["no"][x] += 1
                continue
            # ---
            if len(ta_o) > tab["most"][x]["count"]:
                tab["most"][x]["count"] = len(ta_o)
                tab["most"][x]["q"] = json1["qid"]
                # print(f"most {x}: {json1['qid']}, count: {len(ta_o)}")
            # ---
            for code in ta_o:
                if x == "sitelinks":
                    if code not in tab["sitelinks"]:
                        tab["sitelinks"][code] = 0
                    tab["sitelinks"][code] += 1
                else:
                    if code not in tab["langs"]:
                        tab["langs"][code] = {"labels": 0, "descriptions": 0, "aliases": 0}
                    tab["langs"][code][x] += 1
    # ---
    file_fixed = dump_parts1_fixed / f"{dump_done[1]}.json"
    # ---
    with open(file_fixed, "w", encoding="utf-8") as f:
        json.dump(tab, f)
    # ---
    # file_size = naturalsize(os.path.getsize(items_file), binary=True)
    # print(f"dump_lines size: {file_size}, fixed: {fixed_size}")
    # ---
    fixed_size = naturalsize(os.path.getsize(file_fixed), binary=True)
    # ---
    print(f"dump_lines fixed: {fixed_size}")


def print_memory(i):
    now = time.time()

    print(f"current_count:{i:,}", "time:", now - tt[1])
    tt[1] = now
    # ---
    green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    delta = int(now - time_start)
    print(green % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")


def fix_property(pv):
    return [claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id") for claim in pv if claim.get("mainsnak", {}).get("datatype", "") == "wikibase-item"]


def parse_lines(bz2_file):
    with bz2.open(bz2_file, "r") as f:
        for line in f:
            line = line.decode("utf-8").strip("\n").strip(",")
            if line.startswith("{") and line.endswith("}"):
                yield line


def filter_and_process(entity_dict):
    entity_dict = json.loads(entity_dict)
    # ---
    if entity_dict["type"] == "item":
        claims = entity_dict.get("claims", {})
        line = {
            "qid": entity_dict["title"],
            "labels": list(entity_dict.get("labels", {}).keys()),
            "descriptions": list(entity_dict.get("descriptions", {}).keys()),
            "aliases": list(entity_dict.get("aliases", {}).keys()),
            "sitelinks": list(entity_dict.get("sitelinks", {}).keys()),
        }
        line2 = {
            "qid": entity_dict["title"],
            "claims": {p: fix_property(pv) for p, pv in claims.items() if (
                "all_props" in sys.argv  # or p in most_props
            )},
        }
        # ---
        return line, line2
    # ---
    return None, None


def parse_lines_from_url(url):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        decompressor = bz2.BZ2Decompressor()
        buffer = b""
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                buffer += decompressor.decompress(chunk)
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    line = line.strip().strip(b',')
                    if line.startswith(b"{") and line.endswith(b"}"):
                        yield line.decode('utf-8')
        if buffer.strip().startswith(b"{") and buffer.strip().endswith(b"}"):
            yield buffer.decode('utf-8')


def process_data(bz2_file="", url=""):
    tt[1] = time.time()
    mem_nu = 10000
    dump_numbs = 100000
    # ---
    skip_to = 0
    # ---
    if "skip" in sys.argv:
        js_f = [int(x.name.replace(".json", "").replace("items_", "")) for x in dump_parts1_fixed.glob("*.json")]
        maxfile = max(js_f) if js_f else 0
        skip_to = maxfile * dump_numbs
        dump_done[1] = maxfile
        dump_done["claims"] = maxfile
        print("skip_to:", skip_to, "max file:", maxfile)
    # ---
    print_frist = True
    # ---
    lines = []
    lines_claims = []
    # ---
    if "from_url" in sys.argv:
        print(f"Starting download and processing... {url}")
        data = parse_lines_from_url(url)
    else:
        file_size = os.path.getsize(bz2_file)
        print(naturalsize(file_size, binary=True))
        # ---
        data = parse_lines(bz2_file)
    # ---
    claims_stats = {
        "len_all_props": 0,
        "items_0_claims": 0,
        "items_1_claims": 0,
        "items_no_P31": 0,
        "All_items": 0,
        "total_claims": 0,
    }
    # ---
    # for i, entity_dict in tqdm.tqdm(enumerate(parse_lines(), start=1)):
    for i, entity_dict in enumerate(data, start=1):
        if i < skip_to:
            if i % dump_numbs == 0:
                print("skip_to:", skip_to, "i:", i)
                # print_memory(i)
            continue

        if print_frist:
            print_memory(i)
            print_frist = False
            print("print_frist = False")

        line, line2 = filter_and_process(entity_dict)
        if line:
            lines.append(line)
            lines_claims.append(line2)

        if dump_numbs == len(lines):
            # if i % dump_numbs == 0:
            print(f"dump_lines:{i}, len lines:{len(lines)}")
            print(f"dump_lines_claims:{i}, len lines_claims:{len(lines_claims)}")
            # ---
            dump_lines(lines)
            # ---
            stats = dump_lines_claims(lines_claims)
            # ---
            for x, v in stats.items():
                claims_stats[x] += v
            # ---
            lines_claims.clear()
            lines.clear()
            gc.collect()
            # ---
            ti = time.time() - tt[1]
            # ---
            print_memory(i)
            # ---
            with open(dump_files_dir / "claims_stats.json", "w", encoding="utf-8") as f:
                json.dump(claims_stats, f)
            # ---
            with open(done1_lines, "a", encoding="utf-8") as f:
                f.write(f"done: {i:,} {ti}\n")
            # ---
        elif i % mem_nu == 0:
            print_memory(i)

    # ---
    if lines:
        dump_lines(lines)
    # ---
    if lines_claims:
        stats = dump_lines_claims(lines_claims)
        # ---
        for x, v in stats.items():
            claims_stats[x] += v
        # ---
        with open(dump_files_dir / "claims_stats.json", "w", encoding="utf-8") as f:
            json.dump(claims_stats, f)
    # ---
    print("Processing completed.")


def main():
    time_start2 = time.time()
    # ---
    bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
    # ---
    url = "https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2"
    # ---
    process_data(bz2_file=bz2_file, url=url)
    # ---
    delta = int(time.time() - time_start2)
    # ---
    print(f"read_file: done in {delta}")


if __name__ == "__main__":
    main()
