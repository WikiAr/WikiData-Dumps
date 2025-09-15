"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dir_handler import sitelinks_results_dir

from dir_handler import dump27_dir, dump_files_dir, pids_qids_dir, split_by_pid_dir, most_props_path, dump_dir_claims_fixed, dump_parts1_fixed, results_dir, labels_results_dir


"""
from pathlib import Path


def check_dir(path):
    if not path.exists():
        path.mkdir(parents=True)


main_dir = Path(__file__).parent.parent

dump_files_dir = main_dir / "dump_files"

results_dir = main_dir / "results"
labels_results_dir = main_dir / "results/labels"
claims_results_dir = main_dir / "results/claims"
sitelinks_results_dir = main_dir / "results/sitelinks"

dump27_dir = main_dir / "dump27"

pids_qids_dir = dump_files_dir / "pids_qids"
split_by_pid_dir = dump_files_dir / "split_by_pid"
dump_dir_claims_fixed = dump_files_dir / "parts1_claims_fixed"
dump_parts1_fixed = dump_files_dir / "parts1_fixed"

check_dir(pids_qids_dir)
check_dir(split_by_pid_dir)
check_dir(results_dir)
check_dir(labels_results_dir)
check_dir(claims_results_dir)
check_dir(sitelinks_results_dir)
check_dir(dump_dir_claims_fixed)
check_dir(dump_parts1_fixed)

most_props_path = dump_files_dir / "properties.json"

if not most_props_path.exists():
    most_props_path.write_text('{"P31": 0}')

# most_props = json.loads(most_props_path.read_text())
# # get only first 50 properties after sort
# most_props = {k: v for k, v in sorted(most_props.items(), key=lambda item: item[1], reverse=True)[:50]}
