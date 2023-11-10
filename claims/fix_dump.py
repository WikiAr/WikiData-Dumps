import json
import os
import sys

import tqdm

# ---
try:
    _ = __file__
    DUMP_DIR = "/data/project/himo/dumps"
except Exception:
    DUMP_DIR = "/content/dumps"
# ---
if os.path.exists(r"I:\core\dumps"):
    DUMP_DIR = r"I:\core\dumps"
# ---
print(f"Dump_Dir:{DUMP_DIR}")
# ---
filename = f"{DUMP_DIR}/claims.json"
# ---
files = ["claims_test_fixed.json", "claims_fixed.json"]
# ---
for _f in files:
    if os.path.exists(f"{DUMP_DIR}/{_f}"):
        with open(f"{DUMP_DIR}/{_f}", "w", encoding="utf-8") as f:
            json.dump({}, f)


def fix_props(props):
    # print size of props in memory
    o_size = sys.getsizeof(props)
    # ---
    propsn = {}
    # ---
    for p, pap in tqdm.tqdm(props.items()):
        # "qids": {},"lenth_of_usage": 0,"len_prop_claims": 0,
        # ---
        tab = pap.copy()
        # ---
        # sort by usage
        qids = {
            k: v
            for k, v in sorted(
                tab["qids"].items(), key=lambda item: item[1], reverse=True
            )
        }
        # ---
        if not tab.get("len_of_qids"):
            tab["len_of_qids"] = len(tab["qids"])
        # ---
        maxx = 500 if p == "P31" else 100
        # ---
        # add first 500 properties to dict and other to others
        tab["qids"] = dict(list(qids.items())[:maxx])
        # ---
        others_qids = dict(list(qids.items())[maxx:])
        # ---
        # count others_qids values and add them to others use map lambda
        # others = sum(list(map(lambda x: x[1], others_qids)))
        tab["qids"]["others"] = sum(others_qids.values())
        # ---
        if len(tab["qids"]) > 0:
            propsn[p] = tab
        # ---
        del tab
        del qids
        del others_qids
    # ---
    n_size = sys.getsizeof(propsn)
    # ---
    print(f"o_size:{o_size}, n_size:{n_size}, diff:{n_size-o_size}")
    # ---
    return propsn


def start():
    faf = "claims"
    # ---
    if "test" in sys.argv:
        faf = "claims_test"
    # ---
    filename = f"{Dump_Dir}/{faf}.json"
    # ---
    """python3 wd_core/dump/fix_dumps.py"""
    import json
    import os
    import sys
    
    import tqdm
    
    # ---
    try:
        _ = __file__
        DUMP_DIR = "/data/project/himo/dumps"
    except Exception:
        DUMP_DIR = "/content/dumps"
    # ---
    if os.path.exists(r"I:\core\dumps"):
        DUMP_DIR = r"I:\core\dumps"
    # ---
    print(f"Dump_Dir:{DUMP_DIR}")
    # ---
    filename = f"{DUMP_DIR}/claims.json"
    # ---
    files = ["claims_test_fixed.json", "claims_fixed.json"]
    # ---
    for _f in files:
        if os.path.exists(f"{DUMP_DIR}/{_f}"):
            with open(f"{DUMP_DIR}/{_f}", "w", encoding="utf-8") as f:
                json.dump({}, f)
    
    
    def fix_props(props):
    # ---
    with open(filename, encoding="utf-8") as f:
        data = json.load(f)
    # ---
    data["len_all_props"] = len(data["properties"].keys())
    # ---
    print(f"len_all_props: {data['len_all_props']}")
    # ---
    P31_tab = data["properties"].get("P31", {})
    # ---
    data["properties"] = {
        k: v
        for k, v in sorted(
            data["properties"].items(),
            key=lambda item: item[1]["lenth_of_usage"],
            reverse=True,
        )
    }
    # ---
    if "100" in sys.argv:
        # get only first 100 properties
        first_100 = data["properties"][:100]
        # ---
        if "P31" not in first_100:
            first_100["P31"] = P31_tab
        # ---
        data["properties"] = first_100
    # ---
    props_fixed = fix_props(data["properties"])
    # ---
    data["properties"] = props_fixed
    # ---
    jsonname = f"{Dump_Dir}/{faf}_fixed.json"
    # ---
    with open(jsonname, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile)
    # ---
    print(f"log_dump {jsonname} done..")
    # ---


if __name__ == "__main__":
    start()
