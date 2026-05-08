# NumPy Optimization Plan for dump27 Pipeline

## Pipeline Overview

The dump27 pipeline processes the **Wikidata full dump** (`latest-all.json.bz2`, ~90 GB compressed).  
Each time a **new dump version** is released, the temporary directories are cleared and the pipeline runs fresh.

### Execution Order

```bash
# Step 1 — fetch top WikibaseItem properties via SPARQL
python3 dump27/most_props.py

# Step 2 — stream-parse the full bz2 dump → write temporary shards
python3 dump27/r_28.py

# Step 3a — aggregate label/lang counts from shards
python3 dump27/labels/tab_fixed.py

# Step 3b — render labels wiki-table text
python3 dump27/labels/text.py

# Step 3c — render sitelinks wiki-table text
python3 dump27/sitelinks/text.py

# Step 4a — merge per-PID claim shards
python3 dump27/claims_max/bot.py

# Step 4b — render claims wiki-table text
python3 dump27/claims_max/text.py
```

### Temporary Directories (cleared per dump version)

```
dump_files/pids_qids/            ← output of bot.py
dump_files/split_by_pid/         ← output of r_28.py (per-PID JSONL shards)
dump_files/parts1_claims_fixed/  ← output of r_28.py (per-batch claim stats)
dump_files/parts1_fixed/         ← output of r_28.py (per-batch label stats)
```

These directories **exist and are used during a single pipeline run**.  
They are intentional — clearing them is a manual operation done when a new dump version arrives.

### What Can Be Dropped

The `skip`/resume mechanism in `r_28.py` (`if "skip" in sys.argv`) can be **removed entirely**.  
Since every run processes the dump from scratch, resume logic adds complexity with no benefit.

---

## Current Bottlenecks

### `r_28.py` (the hottest script — processes ~120M entities)

| Bottleneck | Detail |
|---|---|
| Pure-Python dict counters | `tabs_properties[pid]["property_claims_count"] += len(qids)` runs ~120M times |
| QID counting with `dict.get()` | Per-entity loop builds `{qid: count}` dicts with Python hash lookups |
| Two large batch lists | `lines` and `lines_claims` hold 100,000 Python dicts each before flushing |
| `fix_property()` list comprehension | Called once per property per entity — billions of tiny list-comps |

### `claims_max/bot.py` (reads all `split_by_pid/*.json` files)

| Bottleneck | Detail |
|---|---|
| Python dict merge loop | Merges QID→count dicts across thousands of JSONL lines per PID file |
| `sorted()` for top-N | Python sort on large dict items for every PID |

### `labels/tab_fixed.py` (reads all `parts1_fixed/*.json` files)

| Bottleneck | Detail |
|---|---|
| Python dict merge | Merges `lang→{labels, descriptions, aliases}` across thousands of JSON files |

---

## Optimization Plan

Two approaches are described below.  
**Approach 1** keeps the existing file-based architecture and adds NumPy where it helps most.  
**Approach 2** eliminates the intermediate files entirely by accumulating everything in memory.  
Both approaches drop the `skip` mechanism.

---

## Approach 1 — Keep Temp Files, Add NumPy Where It Counts

Minimal change to the pipeline structure. NumPy is added only inside the hot loops.

### 1A. `r_28.py` — Replace dict counters with `np.add.at`

**Target:** `dump_lines_claims()` inner loop over `tabs_properties`.

```python
import numpy as np

# Before processing a batch, build a pid_index for this batch:
pid_list  = sorted(set(pid for line in linesc for pid in line.get("claims", {})))
pid_index = {p: i for i, p in enumerate(pid_list)}
n         = len(pid_list)

claims_count_arr = np.zeros(n, dtype=np.int64)   # property_claims_count
usage_arr        = np.zeros(n, dtype=np.int64)   # len_of_usage / items_with_property

# Inside the batch loop — collect indices and values per entity:
for line in linesc:
    claims = line.get("claims", {})
    if not claims:
        continue
    idx = np.array([pid_index[p] for p in claims], dtype=np.int32)
    val = np.array([len(qids) for qids in claims.values()], dtype=np.int64)
    np.add.at(claims_count_arr, idx, val)
    np.add.at(usage_arr, idx, 1)

# Read results back into tabs_properties:
for pid, i in pid_index.items():
    tabs_properties[pid]["property_claims_count"] += int(claims_count_arr[i])
    tabs_properties[pid]["len_of_usage"]          += int(usage_arr[i])
    tabs_properties[pid]["items_with_property"]   += int(usage_arr[i])
```

**Gain:** Replaces millions of Python dict attribute lookups per batch with C-level `np.add.at`. ~3–5× faster for the stats accumulation inner loop.

### 1B. `r_28.py` — `np.unique` for QID counting

**Target:** The per-PID `qids` dict that counts how many times each QID appears.

```python
# Current (Python):
for qid in qids:
    tabs_properties[pid]["qids"][qid] = \
        tabs_properties[pid]["qids"].get(qid, 0) + 1

# NumPy replacement — collect all QIDs for this PID in the batch,
# then count at flush time:
pid_raw_qids = {pid: [] for pid in pid_list}

for line in linesc:
    for pid, qids in line.get("claims", {}).items():
        pid_raw_qids[pid].extend(qids)

# At flush time:
for pid, raw in pid_raw_qids.items():
    if not raw:
        continue
    arr = np.array(raw)
    unique_qids, counts = np.unique(arr, return_counts=True)
    for q, c in zip(unique_qids.tolist(), counts.tolist()):
        tabs_properties[pid]["qids"][q] = \
            tabs_properties[pid]["qids"].get(q, 0) + c
```

**Gain:** `np.unique` sorts and counts in C. For a batch of 100k entities with dense QID reuse, this is ~5–10× faster than incrementing a Python dict in a loop.

### 1C. `r_28.py` — Remove the `skip` mechanism

```python
# DELETE this entire block — it is dead code without resume support:
if "skip" in sys.argv:
    js_f = [int(x.name.replace(".json", "").replace("items_", ""))
            for x in dump_parts1_fixed.glob("*.json")]
    maxfile = max(js_f) if js_f else 0
    skip_to = maxfile * dump_numbs
    dump_done[1] = maxfile
    dump_done["claims"] = maxfile
    print("skip_to:", skip_to, "max file:", maxfile)
```

Also remove the `if i < skip_to: continue` block inside the main loop.

### 1D. `claims_max/bot.py` — `np.unique` for shard merge

**Target:** `do_lines()` — merges QID→count dicts across thousands of JSONL lines per PID file.

```python
# Collect all (qid, count) pairs for this PID file first:
all_qids   = []
all_counts = []

for line in json1:
    qids_data = line.get("qids", {})
    for qid, cnt in qids_data.items():
        all_qids.append(qid)
        all_counts.append(cnt)

# Aggregate with NumPy:
qids_arr   = np.array(all_qids)
counts_arr = np.array(all_counts, dtype=np.int64)

unique_q, inverse = np.unique(qids_arr, return_inverse=True)
merged = np.zeros(len(unique_q), dtype=np.int64)
np.add.at(merged, inverse, counts_arr)

result_qids = dict(zip(unique_q.tolist(), merged.tolist()))
```

**Gain:** Replaces a Python `dict.get()` loop that runs millions of times per PID file with `np.unique` + `np.add.at` in C. Expected 5–8× speedup per PID file.

### 1E. `claims_max/bot.py` + `claims_max/text.py` — `np.argsort` for top-N

```python
# Current:
sorted_items = sorted(qids_dict.items(), key=lambda x: x[1], reverse=True)[:100]

# NumPy replacement:
keys   = np.array(list(qids_dict.keys()))
values = np.array(list(qids_dict.values()), dtype=np.int64)
order  = np.argsort(values)[::-1]
top_items = list(zip(keys[order[:100]].tolist(), values[order[:100]].tolist()))
```

**Gain:** ~3–5× faster sort for large QID dicts (hundreds of thousands of entries).

### 1F. `labels/tab_fixed.py` — NumPy accumulator for lang counts

```python
import numpy as np

# First pass: collect all lang codes across all files
all_codes = set()
for x in jsonfiles:
    data = ujson.load(open(x))
    all_codes.update(data.get("langs", {}).keys())

lang_list  = sorted(all_codes)
lang_idx   = {c: i for i, c in enumerate(lang_list)}
accumulator = np.zeros((len(lang_list), 3), dtype=np.int64)
# columns: [labels, descriptions, aliases]

# Second pass: accumulate
for x in jsonfiles:
    data = ujson.load(open(x))
    for code, vals in data.get("langs", {}).items():
        i = lang_idx[code]
        accumulator[i, 0] += vals.get("labels", 0)
        accumulator[i, 1] += vals.get("descriptions", 0)
        accumulator[i, 2] += vals.get("aliases", 0)

# Read back into tab["langs"]:
tab["langs"] = {
    code: {
        "labels":       int(accumulator[i, 0]),
        "descriptions": int(accumulator[i, 1]),
        "aliases":      int(accumulator[i, 2]),
    }
    for code, i in lang_idx.items()
}
```

**Gain:** The accumulator lives in a single contiguous int64 block (~120 KB for 5000 lang codes) vs ~1.5 MB of nested Python dict objects. Addition on a NumPy row is faster than three separate Python dict lookups per file.

---

## Approach 2 — Full In-Memory Accumulation (No Intermediate Files)

All accumulators live in memory for the full duration of `r_28.py`. At the end, results are written **directly** to `results/`. This eliminates `tab_fixed.py` and `bot.py` as required pipeline steps.

### Key idea

```
r_28.py  →  results/labels/labels_new.json    (replaces tab_fixed.py)
         →  results/claims/{PID}.json          (replaces bot.py)
```

### Memory layout

```python
# Labels accumulator — lives for the full run
lang_counts     = {}   # lang_code -> np.array([labels, descriptions, aliases], int64)
sitelink_counts = {}   # site_code -> int
no_counts       = np.zeros(4, dtype=np.int64)
# [no_labels, no_descriptions, no_aliases, no_sitelinks]

# Claims accumulator — lives for the full run
pid_index     = {}     # pid_str -> int row index
pid_stats_arr = np.zeros((8000, 3), dtype=np.int64)
# columns: [property_claims_count, len_of_usage, items_with_property]
pid_qids      = {}     # pid -> dict[qid_int -> count]   (int keys = "Q" stripped)

global_stats  = np.zeros(6, dtype=np.int64)
# [All_items, items_with_0_claims, items_with_1_claim,
#  items_missing_P31, total_claims_count, total_properties_count]
```

### QID integer encoding

```python
# "Q12345" -> 12345  (int32, saves ~15x memory vs str)
def qid_to_int(qid: str) -> int:
    return int(qid[1:]) if qid and qid[0] == "Q" else -1

# At output time, convert back:
# 12345 -> "Q12345"
```

### Entity processing (inline, no batch lists)

```python
for entity_dict in parse_lines(bz2_file):
    entity = json.loads(entity_dict)
    if entity["type"] != "item":
        continue

    global_stats[0] += 1  # All_items

    # --- Labels side ---
    for x, i in [("labels", 0), ("descriptions", 1), ("aliases", 2), ("sitelinks", 3)]:
        ta_o = entity.get(x, {})
        if not ta_o:
            no_counts[i] += 1
            continue
        for code in ta_o:
            if x == "sitelinks":
                sitelink_counts[code] = sitelink_counts.get(code, 0) + 1
            else:
                if code not in lang_counts:
                    lang_counts[code] = np.zeros(3, dtype=np.int64)
                lang_counts[code][i] += 1

    # --- Claims side ---
    claims_raw = entity.get("claims", {})
    if not claims_raw:
        global_stats[1] += 1  # items_with_0_claims
        continue

    claims = {p: fix_property(pv) for p, pv in claims_raw.items()}
    claims = {p: v for p, v in claims.items() if v}  # drop empty

    if len(claims) == 1:
        global_stats[2] += 1  # items_with_1_claim
    if "P31" not in claims:
        global_stats[3] += 1  # items_missing_P31

    for pid, qids in claims.items():
        global_stats[4] += len(qids)  # total_claims_count

        if pid not in pid_index:
            pid_index[pid] = len(pid_index)
            if pid_index[pid] >= pid_stats_arr.shape[0]:
                pid_stats_arr = np.vstack(
                    [pid_stats_arr, np.zeros((2000, 3), dtype=np.int64)])
            pid_qids[pid] = {}

        i = pid_index[pid]
        pid_stats_arr[i, 0] += len(qids)
        pid_stats_arr[i, 1] += 1
        pid_stats_arr[i, 2] += 1

        bucket = pid_qids[pid]
        for qid in qids:
            qi = qid_to_int(qid)
            if qi >= 0:
                bucket[qi] = bucket.get(qi, 0) + 1
```

### Write directly to `results/` at end

```python
# Labels
labels_out = {
    "All_items": int(global_stats[0]),
    "no": {"labels": int(no_counts[0]), "descriptions": int(no_counts[1]),
           "aliases": int(no_counts[2]), "sitelinks": int(no_counts[3])},
    "langs": {
        code: {"labels": int(arr[0]), "descriptions": int(arr[1]), "aliases": int(arr[2])}
        for code, arr in lang_counts.items()
    },
    "sitelinks": sitelink_counts,
}
with open(labels_results_dir / "labels_new.json", "w") as f:
    ujson.dump(labels_out, f)

# Claims — one file per PID, written to results/claims/
for pid, bucket in pid_qids.items():
    keys   = np.array(list(bucket.keys()),   dtype=np.int32)
    values = np.array(list(bucket.values()), dtype=np.int32)
    order  = np.argsort(values)[::-1]
    top_k  = order[:500]

    i = pid_index[pid]
    out = {
        "pid": pid,
        "property_claims_count": int(pid_stats_arr[i, 0]),
        "len_of_usage":          int(pid_stats_arr[i, 1]),
        "items_with_property":   int(pid_stats_arr[i, 2]),
        "qids": {f"Q{int(k)}": int(v)
                 for k, v in zip(keys[top_k].tolist(), values[top_k].tolist())},
    }
    with open(claims_results_dir / f"{pid}.json", "w") as f:
        ujson.dump(out, f)
```

In Approach 2, `tab_fixed.py` and `bot.py` are **no longer required** steps. They can be kept as optional standalone tools for rebuilding from temp files if needed.

---

## Comparison

| | Approach 1 (keep temp files) | Approach 2 (full in-memory) |
|---|---|---|
| Code change scope | Small — NumPy only inside hot functions | Large — restructures `r_28.py` main loop |
| Temp files written | Same as today | None |
| Peak RAM | Moderate improvement | ~6–10 GB (most savings from int encoding) |
| Pipeline steps | Same 6 scripts | `r_28.py` alone covers steps 2, 3, 4 |
| `tab_fixed.py` needed | Yes | No (optional) |
| `bot.py` needed | Yes | No (optional) |
| Risk | Low | Medium — needs careful testing |

---

## Implementation Priority (applies to both approaches)

| Priority | Change | Benefit |
|---|---|---|
| 🔴 Critical | Remove `skip` mechanism | Removes dead code, simplifies main loop |
| 🔴 Critical | 1B / A — `np.unique` for QID counting | Biggest speedup in hottest loop |
| 🟠 High | 1A / A — `np.add.at` for PID stats | Replaces millions of Python `+=` calls |
| 🟠 High | 1D — `np.unique` in `bot.py` shard merge | 5–8× faster per PID file |
| 🟡 Medium | 1F — NumPy lang accumulator in `tab_fixed.py` | Faster + less RAM for lang counting |
| 🟡 Medium | 1E — `np.argsort` for top-N sorting | 3–5× faster for large QID dicts |
| 🟢 Optional | Switch to Approach 2 entirely | Maximum RAM and I/O savings |

---

## Required Dependencies

```
numpy >= 1.24    # only new import
ujson            # already used — keep for all JSON I/O
```

---

## Validation

The `test` flag in `r_28.py` sets `dump_numbs = 10_000`:

```bash
python3 dump27/r_28.py test
```

Run this on a small slice, then diff `results/` against the pre-optimization baseline before running on the full 90 GB dump.

Sanity check at end of main loop:

```python
assert int(global_stats[4]) == sum(
    int(pid_stats_arr[i, 0]) for i in range(len(pid_index))
), "total_claims_count mismatch"
```
