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

sys.path.append(str(Path(__file__).parent))

import db_log

db_log.init_db()

most_props_path = Path(__file__).parent.parent / "properties.json"

if not most_props_path.exists():
    most_props_path.write_text('{"q": "", "count": 0}')

most_props = json.loads(most_props_path.read_text())
# get only first 50 properties after sort
most_props = {k: v for k, v in sorted(most_props.items(), key=lambda item: item[1], reverse=True)[:50]}


def check_dir(path):
    if not path.exists():
        path.mkdir()


pids_qids_dir = Path(__file__).parent / "pids_qids"
# --
check_dir(pids_qids_dir)
check_dir(Path(__file__).parent / "jsons")
# --
if "P31" in sys.argv:
    pids_qids_dir = Path(__file__).parent / "pids_qids_P31"
    # --
    check_dir(pids_qids_dir)


class ClaimsProcessor():
    def __init__(self):
        self.memory_check_interval = 80
        self.start_time = time.time()
        self.tt = time.time()
        self.qids_tab = {}

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
            ujson.dump(self.qids_tab, outfile, ensure_ascii=False, indent=2)
        # ---
        print("log_dump done")

    def dump_one_pid(self, pid, tab):
        jsonname = pids_qids_dir / f"{pid}.json"
        # ---
        with open(jsonname, "w", encoding="utf-8") as outfile:
            ujson.dump(tab, outfile, ensure_ascii=False, indent=2)
        # ---
        # print(f"dump_one_pid {pid} done")

    def do_lines(self, json1):
        for x in json1:
            # {"pid":"P282","qids":{"Q8229":2406,"Q82772":77, ... }}
            # ---
            pid = x.get("pid")
            # ---
            if "P31" in sys.argv and pid != "P31":
                continue
            # ---
            if pid not in most_props:
                continue
            # ---
            if pid not in self.qids_tab:
                self.qids_tab[pid] = {"others": 0}
            # ---
            qids = x.get("qids")
            # ---
            for qid, count in qids.items():
                if not qid:
                    continue
                # ---
                if qid not in self.qids_tab[pid]:
                    self.qids_tab[pid][qid] = 0
                # ---
                self.qids_tab[pid][qid] += count
            # ---
            gc.collect()
        # ---
        if "log_db" in sys.argv:
            db_log.log_items(self.qids_tab)
            self.qids_tab = {}
        # ---

    def tab_changes(self):
        # ---
        for x, xx in tqdm.tqdm(self.qids_tab.items(), desc="tab_changes"):
            # ---
            qids_1 = sorted(xx.items(), key=lambda x: x[1], reverse=True)
            # ---
            self.dump_one_pid(x, dict(qids_1))
            # ---
            max_items = 500 if x == "P31" else 100
            # ---
            self.qids_tab[x] = dict(qids_1[:max_items])
            # ---
            others = 0
            others = sum([x[1] for x in qids_1[max_items:]]) if len(qids_1) > max_items else 0
            # ---
            # if len(qids_1) > max_items: others = sum([x[1] for x in qids_1[max_items:]])
            # ---
            self.qids_tab[x]["others"] = others

    def get_lines(self, items_file):
        with open(items_file, "r", encoding="utf-8") as infile:
            for line in infile:
                line = line.strip()
                if line.startswith("{") and line.endswith("}"):
                    yield ujson.loads(line)

    def read_files(self, files):
        print(f"Processing {len(files)} files")
        # ---
        for current_count, file_path in enumerate(tqdm.tqdm(files), 1):
            # ---
            json_data = self.get_lines(file_path)
            # ---
            self.do_lines(json_data)
            # ---

            # ---
            del json_data
            # ---
            gc.collect()
            # ---
            self._print_progress(current_count)
        # ---
        self.tab_changes()
        # ---
        delta = int(time.time() - self.start_time)
        # ---
        print(f"read_files: done in {delta}")
        # ---
        self.log_dump()


if __name__ == "__main__":
    # ---
    parts_dir = Path(__file__).parent / "data_splits"
    # ---
    files = list(parts_dir.glob("*.json"))
    # ---
    processor = ClaimsProcessor()
    # ---
    processor.read_files(files)

# python3 dump1/claims_new/work_splits.py
