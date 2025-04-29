"""

"""


def fix_others(pid, qids_tab, max=0):
    # ---
    max_items = 500 if pid == "P31" else 100
    max_items += 2
    # ---
    if max > 0 :
        max_items = max
    # ---
    if len(qids_tab.items()) > max_items:
        # ---
        others = qids_tab.get("others", 0)
        # ---
        print(f"len of qids: {len(qids_tab.items())}, others: {others}")
        # ---
        if qids_tab.get("others"):
            del qids_tab["others"]
        # ---
        qids_1 = sorted(qids_tab.items(), key=lambda x: x[1], reverse=True)
        # ---
        qids_tab = dict(qids_1[:max_items])
        # ---
        others += sum([x[1] for x in qids_1[max_items:]])
        # ---
        print(f"new others: {others}")
        # ---
        qids_tab["others"] = others
    # ---
    return qids_tab


import json
from pathlib import Path

# file = Path(__file__).parent / "jsons/claims.json"
# with open(file, "r", encoding="utf-8") as f: data = json.load(f)

data = {
    "Q13442814": 500,
    "Q5": 400,
    "Q4167836": 300,
    "Q16521": 200,
    "Q523": 100,
    "others": 150
}

new_data = fix_others("", data, max=2)

print(new_data)
# python3 I:\core\bots\dump_core\dump26\‏‏claims_new\test.py
