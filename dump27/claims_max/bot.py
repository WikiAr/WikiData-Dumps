"""

python I:\core\bots\dump_core\dump26\claims_max\aftter_splits.py


"""
import sys
import time
import gc
import psutil
import os
from pathlib import Path
import ujson
import tqdm
from humanize import naturalsize  # naturalsize(file_size, binary=True)

sys.path.append(str(Path(__file__).parent.parent))

from dir_handler import pids_qids_dir, split_by_pid_dir, claims_results_dir

for file in pids_qids_dir.glob("*.json"):
    file.unlink()
    print(f"deleted {file}")


class ClaimsProcessor():
    def __init__(self):
        self.start_time = time.time()
        self.tt = time.time()
        self.print_at = time.time()
        self.infos = {}
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
            pid = x.get("pid") or m_pid
            # ---
            if pid != m_pid:
                print(f"{pid=} != {m_pid=}")
            # ---
            if pid not in self.qids_tab:
                # initialize new PID bucket
                self.qids_tab[pid] = {"others": 0}
            # ---
            tab = x
            qids = x.get("qids")
            # ---
            if qids.get("qids"):
                # {"pid":"P6216","qids":{"qids":{"Q19652":244},"items_use_it":243,"len_of_usage":243,"len_prop_claims":256}}
                qids = qids.get("qids")
                tab = x.get("qids")
            # ---
            for hh, counts in tab.items():
                if isinstance(counts, int):
                    if hh in self.infos:
                        self.infos[hh] += counts
                    else:
                        self.infos[hh] = counts
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
        if self.qids_tab[pid].get("null"):
            others = self.qids_tab[pid].get("others", 0) + self.qids_tab[pid]["null"]
            # ---
            del self.qids_tab[pid]["null"]
            # ---
            self.qids_tab[pid]["others"] = others
        # ---

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
        self.qids_tab[pid] = dict(sorted(self.qids_tab[pid].items(), key=lambda x: x[1], reverse=True))
        # ---
        self.infos["qids"] = self.qids_tab[pid]
        # ---
        self.dump_one_pid(pid, self.infos)
        # ---
        del json_data
        # ---
        del self.infos["qids"]
        # ---
        self.qids_tab = {}
        # ---
        gc.collect()
        # ---
        delta = int(time.time() - self.start_time)
        # ---
        print(f"read_file: done in {delta}")
        # ---
        return self.infos


def update_pids(tab):
    with open(claims_results_dir / "split_tab.json", "w", encoding="utf-8") as outfile:
        ujson.dump(tab, outfile, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # ---
    start_time = time.time()
    # ---
    files = list(split_by_pid_dir.glob("*.json"))
    # ---
    print(f"Processing {len(files)} files")
    # ---
    # sort files by size
    files.sort(key=lambda x: os.path.getsize(x), reverse=False)
    # ---
    properties_infos = {}
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
        pid_infos = processor.read_file(file_path, pid)
        # ---
        properties_infos[pid] = pid_infos
        # ---
        update_pids(properties_infos)
        # ---
        gc.collect()
    # ---
    properties_infos = dict(sorted(properties_infos.items(), key=lambda x: x[1]["items_use_it"], reverse=True))
    # ---
    delta = int(time.time() - start_time)
    # ---
    print(f"bot done in {delta}")


# python3 I:\core\bots\dump_core\dump27\claims_max\bot.py
