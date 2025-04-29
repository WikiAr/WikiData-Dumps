"""
https://hub-paws.wmcloud.org/user/Mr.%20Ibrahem/lab/tree/dump/claims/tab.py

python I:\core\bots\dump_core\dump26\claims_max\split_new.py

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
# import ijson
import tqdm
from humanize import naturalsize  # naturalsize(file_size, binary=True)


def check_dir(path):
    if not path.exists():
        path.mkdir()


new_splits_dir = Path(__file__).parent / "split_by_pid"
check_dir(new_splits_dir)

most_props_path = Path(__file__).parent.parent / "properties.json"

if not most_props_path.exists():
    most_props_path.write_text('{"q": "", "count": 0}')

most_props = json.loads(most_props_path.read_text())
# get only first 50 properties after sort
most_props = {k: v for k, v in sorted(most_props.items(), key=lambda item: item[1], reverse=True)[:100]}


class ClaimsProcessor:
    def __init__(self, log_dir):
        self.print_at = time.time()
        self.log_dir = log_dir
        self.memory_check_interval = 80
        self.start_time = time.time()
        self.tt = time.time()
        self.properties = {}
        self.properties_qids = {}
        self.table = {
            "delta": 0,
            "len_all_props": 0,
            "items_0_claims": 0,
            "items_1_claims": 0,
            "items_no_P31": 0,
            "All_items": 0,
            "total_claims": 0,
        }

    def _print_progress(self, count: int):
        current_time = time.time()
        print(f"Processed {count} files, elapsed: {current_time - self.tt:.2f}s")
        self.tt = current_time
        self.print_memory()

    def print_memory(self):
        green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"
        usage = psutil.Process(os.getpid()).memory_info().rss / 1024 // 1024
        delta = int(time.time() - self.start_time)
        print(green % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")

    def log_dump(self):
        # ---
        for pid, qids in self.properties_qids.items():
            # ---
            data = {"pid": pid, "qids": qids}
            # ---
            pid_file = self.log_dir / f"{pid}.json"
            # ---
            if not pid_file.exists():
                pid_file.touch()
            # ---
            with open(pid_file, "a", encoding="utf-8") as outfile:
                outfile.write(ujson.dumps(data) + "\n")
            # ---
        print("log_dump done")

    def do_line(self, json1):
        for field in ["All_items", "items_0_claims", "items_1_claims", "items_no_P31", "total_claims"]:
            self.table[field] += json1.get(field, 0)

        claims = json1.get("properties") or json1

        for p, p_qids in claims.items():
            # ---
            if time.time() - self.print_at > 10:
                self.print_at = time.time()
                # self._print_progress(0)
                self.print_memory()
            # ---
            if p not in most_props:
                continue

            if p not in self.properties:
                self.properties_qids[p] = {}
                # ---
                self.properties[p] = {
                    "items_use_it": 0,
                    "lenth_of_usage": 0,
                    "len_of_qids": 0,
                    "len_prop_claims": 0,
                }

            p_qidsx = p_qids.get("qids") or p_qids

            self.properties[p]["lenth_of_usage"] += p_qids.get("lenth_of_usage", 0)
            self.properties[p]["items_use_it"] += p_qids.get("items_use_it", 0)
            self.properties[p]["len_prop_claims"] += p_qids.get("len_prop_claims") or len(p_qidsx)

            # ---
            for qid, count in p_qidsx.items():
                # ---
                if not qid:
                    continue
                # ---
                if qid not in self.properties_qids[p]:
                    self.properties_qids[p][qid] = 0
                # ---
                self.properties_qids[p][qid] += count

            gc.collect()

    def tab_changes(self):
        # ---
        count_total_claims = False
        # ---
        if self.table["total_claims"] == 0:
            count_total_claims = True
        # ---
        for x, xx in self.properties.items():
            # ---
            qids_tab = self.properties_qids.get(x, {})
            # ---
            self.properties[x]["len_of_qids"] += len(qids_tab)
            # ---
            if count_total_claims:
                self.table["total_claims"] += sum(qids_tab.values())
            # ---
            # qids_1 = sorted(qids_tab.items(), key=lambda x: x[1], reverse=True)
            # ---
            max_items = 500 if x == "P31" else 100
            # ---
            # self.properties[x]["qids"] = dict(qids_1[:max_items])
            # ---
            # others = sum([x[1] for x in qids_1[max_items:]]) if len(qids_1) > max_items else 0
            # ---
            # self.properties[x]["qids"]["others"] = 0
        # ---
        self.table["len_all_props"] = len(self.properties)

    def get_lines(self, items_file):
        with open(items_file, "r", encoding="utf-8") as f:
            return ujson.load(f)

    def read_files(self, files):
        # ---
        files_size = sum(os.path.getsize(x) for x in files)
        files_size = naturalsize(files_size, binary=True)
        # ---
        print(f"read_files {files_size=}")
        # ---
        for current_count, file_path in enumerate(tqdm.tqdm(files), 1):
            json_data = self.get_lines(file_path)
            # ---
            self.do_line(json_data)
            # ---
            del json_data
            gc.collect()

            if current_count % self.memory_check_interval == 0:
                self._print_progress(current_count)
        # ---
        self.tab_changes()
        # ---
        delta = int(time.time() - self.start_time)
        # ---
        print(f"read_files: done in {delta}")
        # ---
        self.table["delta"] = f"{delta:,}"
        # ---
        self.log_dump()
        # ---
        self.table["properties"] = self.properties
        # ---
        # self.table["properties_qids"] = self.properties_qids
        # ---
        self._print_progress(current_count)
        # ---
        return self.table


if __name__ == "__main__":
    # ---
    start_time = time.time()
    # ---
    parts_dir = Path(__file__).parent.parent / "parts1_claims_fixed"
    # ---
    files = list(parts_dir.glob("*.json"))
    # ---
    split_by = 32
    # ---
    # python3 claims_max/split.py -split:8
    # ---
    for arg in sys.argv:
        arg, _, value = arg.partition(":")
        if arg == "-split":
            split_by = int(value)
    # ---
    # split to 8 parts
    split_at = len(files) // split_by
    # ---
    # sort files by size
    files.sort(key=lambda x: os.path.getsize(x), reverse=False)
    # ---
    print(f"{len(files)=}, {split_by=}, {split_at=}")
    # ---
    tab = {
        "len_all_props": 0,
        "items_0_claims": 0,
        "items_1_claims": 0,
        "items_no_P31": 0,
        "All_items": 0,
        "total_claims": 0,
        "properties": {},
    }
    # ---
    splits = range(0, len(files), split_at)
    # ---
    for i in splits:
        # ---
        part_files = files[i : i + split_at]
        # ---
        split_num = i // len(part_files)
        # ---
        print(f"Processing {len(files)} files | split number: {split_num} / {len(splits)}")
        # ---
        if "test" in sys.argv:
            continue
        # ---
        processor = ClaimsProcessor(new_splits_dir)
        # ---
        new_data = processor.read_files(part_files)
        # ---
        for x, v in new_data.copy().items():
            # ---
            if isinstance(v, int):
                if x in tab:
                    tab[x] += v
                else:
                    tab[x] = v
            # ---
            if x == "properties":
                # ---
                for prop, prop_tab in v.items():
                    if prop not in tab["properties"]:
                        tab["properties"][prop] = {
                            "items_use_it": 0,
                            "lenth_of_usage": 0,
                            "len_of_qids": 0,
                            "len_prop_claims": 0,
                        }
                    # ---
                    tab["properties"][prop]["items_use_it"] += prop_tab.get("items_use_it", 0)
                    tab["properties"][prop]["lenth_of_usage"] += prop_tab.get("lenth_of_usage", 0)
                    tab["properties"][prop]["len_of_qids"] += prop_tab.get("len_of_qids", 0)
                    tab["properties"][prop]["len_prop_claims"] += prop_tab.get("len_prop_claims", 0)
                # ---
        # ---
        with open(Path(__file__).parent / "split_tab.json", "w", encoding="utf-8") as outfile:
            ujson.dump(tab, outfile)
        # ---
        gc.collect()
    # ---
    delta = int(time.time() - start_time)
    # ---
    print(f"split_new done in {delta}")


# python3 dump1/claims_max/split.py
