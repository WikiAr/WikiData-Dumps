"""

python3 core8/pwb.py I:/core/bots/wd_dumps/qlever_dumps/new/sitelinks/tests/test_sitelinks.py

"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from bot import render

old_data_file = Path(__file__).parent / "texts_test/sitelinks_old.json"
new_data_file = Path(__file__).parent / "texts_test/sitelinks_new.json"

with open(old_data_file, "r", encoding="utf-8") as f:
    old_data = json.load(f)

with open(new_data_file, "r", encoding="utf-8") as f:
    new_data = json.load(f)

sitelinks_data = {
    "new_data": new_data,
    "all_items": 117_416_494,
    "items_without_sitelinks": 83_890_856,
    "file_date": "2025-09-11",
}

render(old_data, sitelinks_data)
