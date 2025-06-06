"""
https://hub-paws.wmcloud.org/user/Mr.%20Ibrahem/lab/tree/dump/claims/tab.py

python3 claims/tab_fixed_new.py

python3 /data/project/himo/bots/dump_core/dump25/claims/tab.py

https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2

"""
import sys
import time
import json
import gc
import psutil
import os
from pathlib import Path
import ujson
import tqdm

most_props_path = Path(__file__).parent.parent / "properties.json"

if not most_props_path.exists():
    most_props_path.write_text('{"q": "", "count": 0}')

most_props = json.loads(most_props_path.read_text())
# get only first 50 properties after sort
most_props = {k: v for k, v in sorted(most_props.items(), key=lambda item: item[1], reverse=True)[:50]}


class ClaimsProcessor():
    def __init__(self):
        self.memory_check_interval = 80
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

    def _print_progress(self, count: int):
        current_time = time.time()
        print(f"Processed {count} files, " f"elapsed: {current_time - self.tt:.2f}s")
        self.tt = current_time
        self.print_memory()

    def print_memory(self):
        green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"
        usage = psutil.Process(os.getpid()).memory_info().rss / 1024 // 1024
        delta = int(time.time() - self.start_time)
        print(green % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")

    def log_dump(self):
        jsonname = Path(__file__).parent / "jsons/claims.json"
        # ---
        if "P31" in sys.argv:
            jsonname = Path(__file__).parent / "jsons/claims_P31.json"
        # ---
        with open(jsonname, "w", encoding="utf-8") as outfile:
            ujson.dump(self.tab, outfile)
        print("log_dump done")

    def _update_counters(self, json1) -> None:
        """Update basic counters from JSON data."""
        for field in ["All_items", "items_0_claims", "items_1_claims", "items_no_P31", "total_claims"]:
            self.tab[field] += json1.get(field, 0)
        self.tab["done"] += json1.get("All_items", 0)

    def _init_property(self, prop: str) -> None:
        """Initialize property structure if not exists."""
        if prop not in self.tab["properties"]:
            self.tab["properties"][prop] = {
                "qids": {"others": 0},
                "items_use_it": 0,
                "lenth_of_usage": 0,
                "len_of_qids": 0,
                "len_prop_claims": 0,
            }

    def _update_property_stats(self, prop, prop_tab) -> None:
        """Update statistics for a single property."""
        p_qids = prop_tab.get("qids") or prop_tab

        self.tab["properties"][prop]["lenth_of_usage"] += prop_tab.get("lenth_of_usage", 0)
        self.tab["properties"][prop]["items_use_it"] += prop_tab.get("items_use_it", 0)
        # ---
        self.tab["properties"][prop]["len_prop_claims"] += len(p_qids)

        for qid, count in p_qids.items():
            if not qid:
                continue
            if qid not in self.tab["properties"][prop]["qids"]:
                self.tab["properties"][prop]["qids"][qid] = 0
            self.tab["properties"][prop]["qids"][qid] += count

            # if qid == "Q5": print(qid, count)

    def do_line(self, json1):
        self._update_counters(json1)

        claims = json1.get("properties") or json1

        for p, p_qids in claims.items():
            if "P31" in sys.argv and p != "P31":
                continue

            if p not in most_props:
                continue

            self._init_property(p)
            self._update_property_stats(p, p_qids)
            gc.collect()

    def tab_changes(self):
        # ---
        count_total_claims = False
        # ---
        if self.tab["total_claims"] == 0:
            count_total_claims = True
        # ---
        for x, xx in self.tab["properties"].items():
            # ---
            self.tab["properties"][x]["len_of_qids"] += len(xx["qids"])
            # ---
            if count_total_claims:
                self.tab["total_claims"] += sum(xx["qids"].values())
            # ---
            qids_1 = sorted(xx["qids"].items(), key=lambda x: x[1], reverse=True)
            # ---
            max_items = 100
            # ---
            if x == "P31":
                max_items = 500
            # ---
            self.tab["properties"][x]["qids"] = dict(qids_1[:max_items])
            # ---
            others = sum([x[1] for x in qids_1[max_items:]]) if len(qids_1) > max_items else 0
            # ---
            self.tab["properties"][x]["qids"]["others"] = others
        # ---
        self.tab["len_all_props"] = len(self.tab["properties"])

    def get_lines(self, items_file):
        with open(items_file, "r", encoding="utf-8") as f:
            return ujson.load(f)

    def read_files(self, files):
        print(f"Processing {len(files)} files")

        for current_count, file_path in enumerate(tqdm.tqdm(files), 1):
            json_data = self.get_lines(file_path)
            self.do_line(json_data)
            del json_data  # ✨ مهم لمسح البيانات فور المعالجة لتقليل الضغط على الذاكرة
            gc.collect()

            if current_count % self.memory_check_interval == 0:
                self._print_progress(current_count)

        self.tab_changes()
        delta = int(time.time() - self.start_time)
        print(f"read_files: done in {delta}")
        self.tab["delta"] = f"{delta:,}"
        self.log_dump()


if __name__ == "__main__":
    # ---
    parts_dir = Path(__file__).parent.parent / "parts1_claims_fixed"
    # ---
    parts_dir = Path(__file__).parent / "claims_new"
    # ---
    files = list(parts_dir.glob("*.json"))
    # ---
    processor = ClaimsProcessor()
    # ---
    processor.read_files(files)
