"""
Approach 2 rewrite: full in-memory accumulation with NumPy.

Changes from original r_28.py:
    - No batch lists (lines / lines_claims removed entirely)
    - No skip/resume mechanism (removed)
    - All properties always processed (no 'all_props' sys.argv flag needed)
    - NumPy arrays for all per-PID stats and QID counting
    - At end, writes outputs directly:
        results/labels/labels_new.json    replaces labels/tab_fixed.py
        dump_files/pids_qids/{PID}.json   replaces claims_max/bot.py
        dump_files/claims_stats.json

Usage:
    python3 core9/pwb.py dump277/r_28.py               # full run
    python3 core9/pwb.py dump277/r_28.py test          # stop after 10,000 items
    python3 core9/pwb.py dump277/r_28.py from_url      # stream from wikimedia URL
"""
import os
import psutil
import json
import ujson
import time
import sys
import bz2
import requests
import numpy as np
from pathlib import Path
from humanize import naturalsize

sys.path.append(str(Path(__file__).parent))

from dir_handler import (
    pids_qids_dir,
    dump_files_dir,
    labels_results_dir,
)

# ─────────────────────────────────────────────────────────────────────────────
# Timers
# ─────────────────────────────────────────────────────────────────────────────

time_start = time.time()
_tt = [time.time()]


def print_memory(i: int):
    now = time.time()
    green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"
    usage = psutil.Process(os.getpid()).memory_info().rss / 1024 // 1024
    delta = int(now - time_start)
    print(f"count:{i:,}  batch:{now - _tt[0]:.1f}s  total:{delta}s")
    print(green % "Memory:", purple % f"{usage} MB")
    _tt[0] = now


# ─────────────────────────────────────────────────────────────────────────────
# In-memory accumulators
# ─────────────────────────────────────────────────────────────────────────────

# ── labels / sitelinks ───────────────────────────────────────────────────────

# lang_code -> int64[3]  : [labels_count, descriptions_count, aliases_count]
lang_counts: dict = {}

# site_code -> int
sitelink_counts: dict = {}

# int64[4]  : [no_labels, no_descriptions, no_aliases, no_sitelinks]
no_counts = np.zeros(4, dtype=np.int64)

most = {
    "labels": {"q": "", "count": 0},
    "descriptions": {"q": "", "count": 0},
    "aliases": {"q": "", "count": 0},
    "sitelinks": {"q": "", "count": 0},
}

# ── claims ───────────────────────────────────────────────────────────────────

# pid -> row index in pid_stats_arr
pid_index: dict = {}

_BLOCK = 4_000
# int64 (n_pids, 3): [property_claims_count, len_of_usage, items_with_property]
pid_stats_arr = np.zeros((_BLOCK, 3), dtype=np.int64)

# pid -> { qid_as_int: count }
# Storing ints instead of "Q12345" strings saves ~15x RAM
pid_qids: dict = {}

# int64[6]:
#   0 All_items
#   1 items_with_0_claims
#   2 items_with_1_claim
#   3 items_missing_P31
#   4 total_claims_count
#   5 total_properties_count  (filled at end)
global_stats = np.zeros(6, dtype=np.int64)

most_claims = {"q": "", "count": 0}
_most_claims_path = dump_files_dir / "most_claims.json"
if _most_claims_path.exists():
    try:
        most_claims = json.loads(_most_claims_path.read_text())
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def fix_property(pv: list) -> list:
    """Return list of wikibase-item QID strings from a raw claim statement list."""
    return [
        claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
        for claim in pv
        if claim.get("mainsnak", {}).get("datatype", "") == "wikibase-item"
    ]


def qid_to_int(qid: str) -> int:
    """'Q12345' -> 12345.  Returns -1 for anything invalid."""
    try:
        if qid and qid[0] in ("Q", "q"):
            return int(qid[1:])
    except (ValueError, IndexError):
        pass
    return -1


def _ensure_pid(pid: str):
    """Lazily register a new PID and grow the stats array if needed."""
    global pid_stats_arr
    if pid not in pid_index:
        idx = len(pid_index)
        pid_index[pid] = idx
        if idx >= pid_stats_arr.shape[0]:
            pid_stats_arr = np.vstack(
                [pid_stats_arr, np.zeros((_BLOCK, 3), dtype=np.int64)]
            )
        pid_qids[pid] = {}


# ─────────────────────────────────────────────────────────────────────────────
# Core entity processor  (one call per JSON line, zero batch buffering)
# ─────────────────────────────────────────────────────────────────────────────

_TATS = [("labels", 0), ("descriptions", 1), ("aliases", 2), ("sitelinks", 3)]


def process_entity(raw: str):
    global most_claims

    try:
        entity = json.loads(raw)
    except json.JSONDecodeError:
        return

    if entity.get("type") != "item":
        return

    qid = entity.get("title", "")
    global_stats[0] += 1   # All_items

    # ── labels / sitelinks ───────────────────────────────────────────────────
    for key, col in _TATS:
        ta_o = entity.get(key, {})
        n = len(ta_o)
        if n == 0:
            no_counts[col] += 1
            continue
        if n > most[key]["count"]:
            most[key]["count"] = n
            most[key]["q"] = qid
        for code in ta_o:
            if key == "sitelinks":
                sitelink_counts[code] = sitelink_counts.get(code, 0) + 1
            else:
                if code not in lang_counts:
                    lang_counts[code] = np.zeros(3, dtype=np.int64)
                lang_counts[code][col] += 1

    # ── claims ───────────────────────────────────────────────────────────────
    raw_claims = entity.get("claims", {})

    # Build {pid: [qid, ...]} keeping only non-empty wikibase-item values
    claims: dict = {}
    for p, pv in raw_claims.items():
        qs = [x for x in fix_property(pv) if x]
        if qs:
            claims[p] = qs

    n_props = len(claims)

    if n_props == 0:
        global_stats[1] += 1   # items_with_0_claims
        return

    if n_props == 1:
        global_stats[2] += 1   # items_with_1_claim

    if "P31" not in claims:
        global_stats[3] += 1   # items_missing_P31

    if n_props > most_claims["count"]:
        most_claims = {"q": qid, "count": n_props}

    # Collect (pid_idx, claim_count) pairs for this entity then apply
    # np.add.at in one vectorised call — faster than looping pid_stats_arr.
    batch_idx = []
    batch_len = []

    for pid, qs in claims.items():
        global_stats[4] += len(qs)   # total_claims_count
        _ensure_pid(pid)
        idx = pid_index[pid]
        batch_idx.append(idx)
        batch_len.append(len(qs))

        bucket = pid_qids[pid]
        for qid_val in qs:
            qi = qid_to_int(qid_val)
            if qi >= 0:
                bucket[qi] = bucket.get(qi, 0) + 1

    idx_arr = np.array(batch_idx, dtype=np.int32)
    len_arr = np.array(batch_len, dtype=np.int64)
    np.add.at(pid_stats_arr[:, 0], idx_arr, len_arr)   # property_claims_count
    np.add.at(pid_stats_arr[:, 1], idx_arr, 1)          # len_of_usage
    np.add.at(pid_stats_arr[:, 2], idx_arr, 1)          # items_with_property


# ─────────────────────────────────────────────────────────────────────────────
# Output writers
# ─────────────────────────────────────────────────────────────────────────────

def write_labels_new():
    """
    Write results/labels/labels_new.json.
    Identical format to what labels/tab_fixed.py produced.
    labels/text.py and sitelinks/text.py read this file unchanged.
    """
    out = {
        "All_items": int(global_stats[0]),
        "no": {
            "labels": int(no_counts[0]),
            "descriptions": int(no_counts[1]),
            "aliases": int(no_counts[2]),
            "sitelinks": int(no_counts[3]),
        },
        "most": most,
        "langs": {
            code: {
                "labels": int(arr[0]),
                "descriptions": int(arr[1]),
                "aliases": int(arr[2]),
            }
            for code, arr in lang_counts.items()
        },
        "sitelinks": sitelink_counts,
    }
    path = labels_results_dir / "labels_new.json"
    with open(path, "w", encoding="utf-8") as f:
        ujson.dump(out, f)
    print(f"  labels_new.json  ({path})")


def write_pids_qids():
    """
    Write dump_files/pids_qids/{PID}.json for every PID.
    Identical format to what claims_max/bot.py produced.
    claims_max/text.py reads these files unchanged.

    Per-file format:
      {
        "pid": "P31",
        "property_claims_count": N,
        "len_of_usage": N,
        "items_with_property": N,
        "qids": {"Q5": 12345, "Q4167410": 5678, ..., "others": 99}
      }

    Uses np.argsort for the top-N sort (faster than Python sorted on large dicts).
    """
    global_stats[5] = len(pid_index)   # total_properties_count
    n_pids = len(pid_index)
    print(f"  Writing {n_pids:,} PID files -> {pids_qids_dir}")

    for pid, idx in pid_index.items():
        bucket = pid_qids[pid]
        if not bucket:
            continue

        # P31 gets 500 rows; all others get 102  (matching original bot.py logic)
        max_items = 500 if pid == "P31" else 102

        keys_arr = np.array(list(bucket.keys()), dtype=np.int32)
        values_arr = np.array(list(bucket.values()), dtype=np.int32)

        order = np.argsort(values_arr)[::-1]   # descending by count

        if len(values_arr) > max_items:
            others_total = int(values_arr[order[max_items:]].sum())
            top = order[:max_items]
        else:
            others_total = 0
            top = order

        top_keys = keys_arr[top]
        top_values = values_arr[top]

        # Convert int keys back to "Q{n}" strings
        qids_out = {
            f"Q{int(k)}": int(v)
            for k, v in zip(top_keys, top_values)
        }
        if others_total:
            qids_out["others"] = others_total

        out = {
            "pid": pid,
            "property_claims_count": int(pid_stats_arr[idx, 0]),
            "len_of_usage": int(pid_stats_arr[idx, 1]),
            "items_with_property": int(pid_stats_arr[idx, 2]),
            "qids": qids_out,
        }

        path = pids_qids_dir / f"{pid}.json"
        with open(path, "w", encoding="utf-8") as f:
            ujson.dump(out, f, ensure_ascii=False, indent=2)

    print(f"  pids_qids/ done  ({n_pids:,} files)")


def write_claims_stats():
    """
    Write dump_files/claims_stats.json.
    Identical format to before — claims_max/text.py reads it unchanged.
    """
    stats = {
        "All_items": int(global_stats[0]),
        "items_with_0_claims": int(global_stats[1]),
        "items_with_1_claim": int(global_stats[2]),
        "items_missing_P31": int(global_stats[3]),
        "total_claims_count": int(global_stats[4]),
        "total_properties_count": int(global_stats[5]),
    }
    path = dump_files_dir / "claims_stats.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"  claims_stats.json  ({path})")
    for k, v in stats.items():
        print(f"    {k}: {v:,}")


# ─────────────────────────────────────────────────────────────────────────────
# Stream parsers
# ─────────────────────────────────────────────────────────────────────────────

def parse_lines(bz2_file: str):
    with bz2.open(bz2_file, "r") as f:
        for line in f:
            line = line.decode("utf-8").strip("\n").strip(",")
            if line.startswith("{") and line.endswith("}"):
                yield line


def parse_lines_from_url(url: str):
    session = requests.session()
    session.headers.update({
        "User-Agent": "Himo bot/1.0 (https://himo.toolforge.org/; tools.himo@toolforge.org)"
    })
    with session.get(url, stream=True) as response:
        response.raise_for_status()
        decompressor = bz2.BZ2Decompressor()
        buffer = b""
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                buffer += decompressor.decompress(chunk)
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line = line.strip().strip(b",")
                    if line.startswith(b"{") and line.endswith(b"}"):
                        yield line.decode("utf-8")
        tail = buffer.strip()
        if tail.startswith(b"{") and tail.endswith(b"}"):
            yield tail.decode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def process_data(bz2_file: str = "", url: str = ""):
    _tt[0] = time.time()

    is_test = "test" in sys.argv
    from_url = "from_url" in sys.argv

    mem_nu = 1_000 if is_test else 10_000
    test_limit = 10_000 if is_test else None

    if from_url:
        print(f"Streaming from URL: {url}")
        data = parse_lines_from_url(url)
    else:
        file_size = os.path.getsize(bz2_file)
        print(f"File: {bz2_file}")
        print(f"Size: {naturalsize(file_size, binary=True)}")
        data = parse_lines(bz2_file)

    print("Starting inline processing (no batch lists) ...")
    i = 0
    for i, raw in enumerate(data, start=1):
        process_entity(raw)

        if i % mem_nu == 0:
            print_memory(i)

        if test_limit and i >= test_limit:
            print(f"[test] stopping at {i:,} raw lines")
            break

    print("\nStream finished.")
    print(f"  Raw lines seen : {i:,}")
    print(f"  Items (type=item): {int(global_stats[0]):,}")
    print_memory(i)


def main():
    bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
    url = "https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2"

    # ── parse the dump ───────────────────────────────────────────────────────
    process_data(bz2_file=bz2_file, url=url)

    # ── sanity check ─────────────────────────────────────────────────────────
    n_pids = len(pid_index)
    per_pid_total = int(pid_stats_arr[:n_pids, 0].sum())
    global_total = int(global_stats[4])
    if per_pid_total != global_total:
        print(f"WARNING claims mismatch: per-PID={per_pid_total:,}  global={global_total:,}")
    else:
        print(f"OK claims sanity check passed ({global_total:,} total claims)")

    # ── write all outputs ────────────────────────────────────────────────────
    print("\n-- Writing outputs --")
    write_labels_new()    # -> results/labels/labels_new.json
    write_pids_qids()     # -> dump_files/pids_qids/{PID}.json
    write_claims_stats()  # -> dump_files/claims_stats.json

    _most_claims_path.write_text(json.dumps(most_claims))
    print(f"  most_claims.json  ({_most_claims_path})")

    delta = int(time.time() - time_start)
    print(f"\nDone. r_28.py completed in {delta:,} seconds")


if __name__ == "__main__":
    main()
