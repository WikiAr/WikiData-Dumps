"""

python I:\core\bots\dump_core\dump26\claims_max\aftter_splits.py


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
from humanize import naturalsize  # naturalsize(file_size, binary=True)

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


class ClaimsProcessor():
    def __init__(self):
        self.start_time = time.time()
        self.tt = time.time()
        self.print_at = time.time()
        self.qids_tab = {}

    def _print_progress(self, count: int):
        current_time = time.time()
        print(f"Processed {count}, " f"elapsed: {current_time - self.tt:.2f}s")
        self.tt = current_time
        self.print_memory()

    def print_memory(self):
        green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"
        usage = psutil.Process(os.getpid()).memory_info().rss / 1024 // 1024
        delta = int(time.time() - self.start_time)
        print(green % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")

    def dump_one_pid(self, pid, tab):
        jsonname = pids_qids_dir / f"{pid}.json"
        # ---
        tab = dict(sorted(tab.items(), key=lambda x: x[1], reverse=True))
        # ---
        with open(jsonname, "w", encoding="utf-8") as outfile:
            ujson.dump(tab, outfile, ensure_ascii=False, indent=2)

    def do_lines(self, json1, m_pid):
        # ---
        for n, x in enumerate(json1):
            # {"pid":"P282","qids":{"Q8229":2406,"Q82772":77, ... }}
            # ---
            if time.time() - self.print_at > 5:
                self.print_at = time.time()
                self._print_progress(n)
            # ---
            pid = x.get("pid")
            # ---
            if pid != m_pid:
                print(f"{pid=} != {m_pid=}")
            # ---
            if pid not in self.qids_tab:
                # initialize new PID bucket
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

    def get_lines(self, items_file):
        with open(items_file, "r", encoding="utf-8") as infile:
            for line in infile:
                line = line.strip()
                if line.startswith("{") and line.endswith("}"):
                    yield ujson.loads(line)

    def read_file(self, file_path, pid):
        # ---
        pid = file_path.name.replace(".json", "")
        # ---
        json_data = self.get_lines(file_path)
        # ---
        # if pid not in most_props: return
        # ---
        if pid not in self.qids_tab:
            self.qids_tab[pid] = {"others": 0}
        # ---
        self.do_lines(json_data, pid)
        # ---
        self._print_progress(1)
        # ---
        self.dump_one_pid(pid, self.qids_tab[pid])
        # ---
        del json_data
        del self.qids_tab[pid]
        # ---
        gc.collect()
        # ---
        delta = int(time.time() - self.start_time)
        # ---
        print(f"read_file: done in {delta}")


if __name__ == "__main__":
    # ---
    start_time = time.time()
    # ---
    parts_dir = Path(__file__).parent / "split_by_pidxx"
    # ---
    files = list(parts_dir.glob("*.json"))
    # ---
    print(f"Processing {len(files)} files")
    # ---
    # sort files by size
    files.sort(key=lambda x: os.path.getsize(x), reverse=False)
    # ---
    for i, file_path in enumerate(tqdm.tqdm(files), 1):
        # ---
        pid = file_path.name.replace(".json", "")
        # ---
        file_size = naturalsize(os.path.getsize(file_path), binary=True)
        # ---
        print(f"Processing {pid=}, {file_size=}")
        # ---
        if "P31" in sys.argv and pid != "P31":
            continue
        # ---
        processor = ClaimsProcessor()
        # ---
        processor.read_file(file_path, pid)
        # ---
        gc.collect()
    # ---
    delta = int(time.time() - start_time)
    # ---
    print(f"after_splits done in {delta}")


# python3 dump1/claims_max/after_splits.py
