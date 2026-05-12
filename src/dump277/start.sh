#!/bin/bash
#
# Full pipeline — Approach 2 (in-memory NumPy accumulation)
#
# Step 2 (r_28.py) now covers what tab_fixed.py and bot.py used to do,
# so those two scripts are no longer part of the pipeline.
#
# Output written directly to results/ at the end of r_28.py:
#   results/labels/labels_new.json    (was: labels/tab_fixed.py)
#   dump_files/pids_qids/{PID}.json   (was: claims_max/bot.py)
#   dump_files/claims_stats.json

set -e   # stop on first error

# Step 1 — fetch top WikibaseItem properties via SPARQL
python3 c9/pwb.py dump277/most_props.py

# Step 2 — stream-parse the full dump + accumulate all stats in memory
#           writes labels_new.json, pids_qids/, and claims_stats.json
python3 c9/pwb.py dump277/r_28.py

# Step 3 — labels wiki-table text  (reads results/labels/labels_new.json)
python3 c9/pwb.py dump277/labels/text.py

# Step 4 — sitelinks wiki-table text  (reads results/labels/labels_new.json)
python3 c9/pwb.py dump277/sitelinks/text.py

# Step 5 — claims wiki-table text  (reads dump_files/pids_qids/ and claims_stats.json)
python3 c9/pwb.py dump277/claims_max/text.py
