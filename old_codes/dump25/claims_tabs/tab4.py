"""
python3 dump/claims_tabs/tab4.py
python3 dump/claims_tabs/tab4.py numb:1 len:413
python3 dump/claims_tabs/tab4.py numb:2 len:413
python3 dump/claims_tabs/tab4.py numb:3 len:413
python3 dump/claims_tabs/tab4.py numb:4 len:413
python3 dump/claims_tabs/tab4.py numb:5 len:413
python3 dump/claims_tabs/tab4.py numb:6 len:413
python3 dump/claims_tabs/tab4.py numb:7 len:413

python3 dump/claims_tabs/tab4.py numb:8 len:413
python3 dump/claims_tabs/tab4.py numb:9 len:413
python3 dump/claims_tabs/tab4.py numb:10 len:413
python3 dump/claims_tabs/tab4.py numb:11 len:413

"""
import sys
import time
import psutil
import os
from pathlib import Path
import ujson
import tqdm
import gc
from humanize import naturalsize

# ---
Dir = Path(__file__).parent.parent
# ---
dump_dir = Dir / "parts_claims"
# ---
if not dump_dir.exists():
    dump_dir.mkdir()

with open(Path(__file__).parent / "lists.json", "r", encoding="utf-8") as f:
    lists = ujson.load(f)


class ClaimsProcessor:
    def __init__(self, parts_dir, numb=10):
        self.memory_print = 100000
        self.dump_numb = 59
        self.dump_done = 0
        # ---
        self.parts_dir = parts_dir
        self.jsonfiles = []
        # ---
        self.start_time = time.time()
        self.tt = time.time()
        # ---
        self.numb = numb if numb else 10
        # ---
        self.current_count = 0
        # ---
        self.done = 0
        # ---
        self.get_jsons()
        # ---
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

    def get_jsons(self):
        # ---
        jsons = lists.get(self.numb) or lists.get(str(self.numb))
        # ---
        if not jsons:
            print(f"list not found: {self.numb}")
            exit(1)
        # ---
        self.jsonfiles = [self.parts_dir / x for x in jsons]
        # ---
        print(f"all json files: {len(self.jsonfiles)}")

    def dump_lines(self):
        # ---
        if not self.tab["properties"]:
            return
        # ---
        self.dump_done += 1
        # ---
        items_file = dump_dir / f"{self.numb}_{self.dump_done}.json"
        # ---
        with open(items_file, "w", encoding="utf-8") as f:
            ujson.dump(self.tab, f)
        # ---
        print(f"dump_lines done file: {items_file}.")
        # ---
        del self.tab
        # ---
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
        gc.collect()

    def print_memory(self, cc):
        print(cc, time.time() - self.tt)
        self.tt = time.time()

        green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"
        usage = psutil.Process(os.getpid()).memory_info().rss
        usage = naturalsize(usage, binary=True)
        delta = int(time.time() - self.start_time)

        print(green % "Memory usage:", purple % f"{usage}", f"time: to now {delta}")

    def do_line(self, json1):
        self.tab["All_items"] += 1
        self.done += 1
        claims = json1.get("claims", {})
        claims_length = len(claims)

        if claims_length == 0:
            self.tab["items_with_0_claims"] += 1
            del claims, json1
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
            # ---
            del p_tab
        # ---
        if p_qids:
            del p_qids
        # ---
        del claims, json1

    def get_lines(self, items_file):
        with open(items_file, "r", encoding="utf-8") as f:
            for line in ujson.load(f):
                yield line

    def read_file(self):
        # ---
        current_count = self.current_count
        # ---
        xn = 0
        # ---
        for x in tqdm.tqdm(self.jsonfiles):
            # ---
            xn += 1
            # ---
            lines = self.get_lines(x)
            # ---
            # for current_count, line in tqdm.tqdm(enumerate(lines, start=current_count)):
            for current_count, line in enumerate(lines, start=current_count):
                self.do_line(line)
                # ---
                if current_count % self.memory_print == 0:
                    self.print_memory(current_count)
                # ---
                del line
            # ---
            if xn % self.dump_numb == 0:
                self.print_memory(current_count)
                # ---
                self.dump_lines()
                # ---
                self.print_memory(current_count)
            # ---
            del lines
        # ---
        print(f"all_items: {current_count}")
        print(f"read all lines: {self.done}")
        # ---
        delta = int(time.time() - self.start_time)
        # ---
        print(f"read_file: done in {delta}")
        # ---
        self.dump_lines()


if __name__ == "__main__":
    # ---
    parts_dir = Dir / "parts"
    # ---
    numb = 0
    # ---
    for arg in sys.argv:
        arg, _, vaule = arg.partition(":")
        if arg == "numb":
            numb = int(vaule)
    # ---
    processor = ClaimsProcessor(parts_dir, numb=numb)
    processor.read_file()
