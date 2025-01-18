"""
https://hub-paws.wmcloud.org/user/Mr.%20Ibrahem/lab/tree/dump/claims/tab.py

python3 dump/claims/tab.py

python3 /data/project/himo/bots/dump_core/dump25/claims/tab.py

https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2

"""
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
        self.tab_oginal = {
            "labels": {"ar": 0, "en": 0},
            "descriptions": {"ar": 0, "en": 0},
            "aliases": {"ar": 0, "en": 0},
            "sitelinks": {"arwiki": 0, "enwiki": 0},
            "claims": {"P31": {"Q5": 0}},
        }
        self.tab = self.tab_oginal.copy()

    def print_memory(self):
        yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"
        usage = psutil.Process(os.getpid()).memory_info().rss / 1024 // 1024
        delta = int(time.time() - self.start_time)
        print(yellow % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")

    def log_dump(self):
        jsonname = Path(__file__).parent / "claims.json"
        with open(jsonname, "w", encoding="utf-8") as outfile:
            ujson.dump(self.tab, outfile)
        print("log_dump done")

    def do_line(self, json1):
        self.tab["All_items"] += 1
        self.tab["done"] += 1
        _line = {
            "labels": ["ar", "en"],
            "descriptions": ["ar", "en"],
            "aliases": ["ar", "en"],
            "sitelinks": ["arwiki", "enwiki"],
            "claims": {"P31": ["Q80", "Q90"]},
        }
        claims = json1.get("claims", {})
        claims_length = len(claims)

        if claims_length == 0:
            self.tab["items_0_claims"] += 1
            return

        if claims_length == 1:
            self.tab["items_1_claims"] += 1

        if "P31" not in claims:
            self.tab["items_no_P31"] += 1

        for p, p_qids in claims.items():
            self.tab["total_claims"] += len(p_qids)
            p_tab = self.tab["properties"].get(
                p,
                {
                    "qids": {"others": 0},
                    "lenth_of_usage": 0,
                    "len_prop_claims": 0,
                },
            )

            p_tab["lenth_of_usage"] += 1
            p_tab["len_prop_claims"] += len(p_qids)

            for qid in p_qids:
                if qid:
                    p_tab["qids"][qid] = p_tab["qids"].get(qid, 0) + 1

            self.tab["properties"][p] = p_tab

    def get_lines(self, items_file):
        with open(items_file, "r", encoding="utf-8") as f:
            for line in ujson.load(f):
                yield line

    def read_file(self, parts_dir):
        jsonfiles = list(parts_dir.glob("*.json"))
        print(f"all json files: {len(jsonfiles)}")
        # ---
        cc = 1
        # ---
        for x in tqdm.tqdm(jsonfiles):
            lines = self.get_lines(x)
            # ---
            for cc, line in tqdm.tqdm(enumerate(lines, start=cc)):
                self.do_line(line)
                # ---
                if cc % 100000 == 0:
                    print(cc, time.time() - self.tt)
                    self.tt = time.time()
                    self.print_memory()
        # ---
        print(f"all_items: {cc}")
        print(f"read all lines: {self.tab['done']}")
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
