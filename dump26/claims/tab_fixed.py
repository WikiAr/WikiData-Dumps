"""
https://hub-paws.wmcloud.org/user/Mr.%20Ibrahem/lab/tree/dump/claims/tab.py

python3 dump/claims/tab.py

python3 /data/project/himo/bots/dump_core/dump25/claims/tab.py

https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2

"""
import sys
import time
import psutil
import os
from pathlib import Path
import ujson
import tqdm


class ClaimsProcessor:
    def __init__(self):
        self.start_time = time.time()
        self.tt = time.time()
        self.tab = {
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
        }

    def print_memory(self):
        green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"
        usage = psutil.Process(os.getpid()).memory_info().rss / 1024 // 1024
        delta = int(time.time() - self.start_time)
        print(green % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")

    def log_dump(self):
        jsonname = Path(__file__).parent / "claims.json"
        # ---
        if "P31" in sys.argv:
            jsonname = Path(__file__).parent / "claims_P31.json"
        # ---
        with open(jsonname, "w", encoding="utf-8") as outfile:
            ujson.dump(self.tab, outfile)
        print("log_dump done")

    def do_line(self, json1):
        self.tab["All_items"] += json1.get("All_items", 0)
        self.tab["done"] += json1.get("All_items", 0)
        # ---
        self.tab["items_0_claims"] += json1.get("items_0_claims", 0)
        self.tab["items_1_claims"] += json1.get("items_1_claims", 0)
        self.tab["items_no_P31"] += json1.get("items_no_P31", 0)
        self.tab["total_claims"] += json1.get("total_claims", 0)

        claims = json1.get("properties") or json1

        for p, p_qids in claims.items():
            if "P31" in sys.argv and p != "P31":
                continue

            if p not in self.tab["properties"]:
                self.tab["properties"][p] = {
                    "qids": {"others": 0},
                    "lenth_of_usage": 0,
                    "len_prop_claims": 0,
                }

            self.tab["properties"][p]["lenth_of_usage"] += 1
            self.tab["properties"][p]["len_prop_claims"] += len(p_qids)

            for qid in p_qids:
                if not qid:
                    continue
                # ----
                if qid not in self.tab["properties"][p]["qids"]:
                    self.tab["properties"][p]["qids"][qid] = 0
                # ----
                self.tab["properties"][p]["qids"][qid] += p_qids[qid]
                # if qid == "Q5": print(qid, p_qids[qid])

    def tab_changes(self):
        # ---
        count_total_claims = False
        # ---
        if self.tab["total_claims"] == 0:
            count_total_claims = True
        # ---
        for x, xx in self.tab["properties"].items():
            # ---
            self.tab["properties"][x]["len_of_qids"] = len(xx["qids"])
            # ---
            if count_total_claims:
                self.tab["total_claims"] += sum(xx["qids"].values())
            # ---
            qids_1 = sorted(xx["qids"].items(), key=lambda x: x[1], reverse=True)
            # ---
            self.tab["properties"][x]["qids"] = dict(qids_1[:100])
            # ---
            others = sum([x[1] for x in qids_1[100:]]) if len(qids_1) > 100 else 0
            # ---
            self.tab["properties"][x]["qids"]["others"] = others
        # ---
        self.tab["len_all_props"] = len(self.tab["properties"])

    def get_lines(self, items_file):
        with open(items_file, "r", encoding="utf-8") as f:
            return ujson.load(f)

    def read_file(self, parts_dir):
        jsonfiles = list(parts_dir.glob("*.json"))
        print(f"all json files: {len(jsonfiles)}")
        # ---
        current_count = 1
        # ---
        for x in tqdm.tqdm(jsonfiles):
            # ---
            current_count += 1
            # ---
            line = self.get_lines(x)
            # ---
            self.do_line(line)
            # ---
            if current_count % 500 == 0:
                print(current_count, time.time() - self.tt)
                self.tt = time.time()
                self.print_memory()
        # ---
        print(f"all_items: {current_count}")
        print(f"read all lines: {self.tab['done']}")
        # ---
        self.tab_changes()
        # ---
        delta = int(time.time() - self.start_time)
        # ---
        print(f"read_file: done in {delta}")
        # ---
        self.tab["delta"] = f"{delta:,}"
        # ---
        self.log_dump()


if __name__ == "__main__":
    Dir = Path(__file__).parent.parent
    # ---
    parts_dir = Dir / "parts1_claims_fixed"
    # ---
    processor = ClaimsProcessor()
    processor.read_file(parts_dir)
