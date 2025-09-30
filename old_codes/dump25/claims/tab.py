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
            "total_properties_count": 0,
            "items_with_0_claims": 0,
            "items_with_1_claim": 0,
            "items_missing_P31": 0,
            "All_items": 0,
            "total_claims_count": 0,
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
        self.tab["All_items"] += 1
        self.tab["done"] += 1
        claims = json1.get("claims", {})
        claims_length = len(claims)

        if claims_length == 0:
            self.tab["items_with_0_claims"] += 1
            return

        if claims_length == 1:
            self.tab["items_with_1_claim"] += 1

        if "P31" not in claims:
            self.tab["items_missing_P31"] += 1

        for p, p_qids in claims.items():
            if "P31" in sys.argv and p != "P31":
                continue

            self.tab["total_claims_count"] += len(p_qids)
            p_tab = self.tab["properties"].get(
                p,
                {
                    "qids": {"others": 0},
                    "lenth_of_usage": 0,
                    "property_claims_count": 0,
                },
            )

            p_tab["lenth_of_usage"] += 1
            p_tab["property_claims_count"] += len(p_qids)

            for qid in p_qids:
                if qid:
                    p_tab["qids"][qid] = p_tab["qids"].get(qid, 0) + 1

            self.tab["properties"][p] = p_tab

    def tab_changes(self):
        # ---
        for x, xx in self.tab["properties"].items():
            # ---
            self.tab["properties"][x]["unique_qids_count"] = len(xx["qids"])
            # ---
            qids_1 = sorted(xx["qids"].items(), key=lambda x: x[1], reverse=True)
            # ---
            self.tab["properties"][x]["qids"] = dict(qids_1[:100])
            # ---
            self.tab["properties"][x]["qids"]["others"] = xx["qids"].get("others", 0)
        # ---
        self.tab["total_properties_count"] = len(self.tab["properties"])

    def get_lines(self, items_file):
        with open(items_file, "r", encoding="utf-8") as f:
            for line in ujson.load(f):
                yield line

    def read_file(self, parts_dir):
        jsonfiles = list(parts_dir.glob("*.json"))
        print(f"all json files: {len(jsonfiles)}")
        # ---
        current_count = 1
        # ---
        for x in tqdm.tqdm(jsonfiles):
            lines = self.get_lines(x)
            # ---
            for current_count, line in tqdm.tqdm(enumerate(lines, start=current_count)):
                self.do_line(line)
                # ---
                if current_count % 100000 == 0:
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
    parts_dir = Dir / "parts"
    # ---
    processor = ClaimsProcessor()
    processor.read_file(parts_dir)
