"""

python3 core8/pwb.py I:/core/bots/wd_dumps/qlever_dumps/tests/test_sitelinks_texts.py

"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from texts_sites import make_text

data_file = Path(__file__).parent.parent / "dumps/sitelinks.json"

with open(data_file, "r", encoding="utf-8") as f:
    n_tab = json.load(f)

text = make_text(n_tab)

text_file = Path(__file__).parent / "texts_test/text.txt"

with open(text_file, "w", encoding="utf-8") as f:
    f.write(text)
