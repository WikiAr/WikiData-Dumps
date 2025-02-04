"""

python3 dump/claims_tabs/list.py

"""
import json
from pathlib import Path

Dir = Path(__file__).parent.parent

parts_dir = Dir / "parts"
# ---
jsonfiles = list(parts_dir.glob("*.json"))
# ---
# sort list by number
jsonfiles.sort(key=lambda x: int(x.stem.replace("items_", "")))
# ---
# for n, x in enumerate(jsonfiles, start=1): print(n, x)
# ---
# split the list to 10 lists
len_of_list = len(jsonfiles) // 11
lists = [jsonfiles[i : i + len_of_list] for i in range(0, len(jsonfiles), len_of_list)]
# ---
dict_lists = {}
# ---
for n, x in enumerate(lists, start=1):
    print(n, len(x))
    dict_lists[n] = [str(y.name) for y in x]
# ---
with open(Path(__file__).parent / "lists.json", "w", encoding="utf-8") as f:
    json.dump(dict_lists, f, indent=2, ensure_ascii=False)

for x in dict_lists:
    print(f"python3 dump/claims_tabs/tab4.py numb:{x} len:{len(dict_lists[x])}")
