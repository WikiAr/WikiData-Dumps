"""

python3 core8/pwb.py I:/core/bots/dump_core/qlever_dumps/props/bot.py oldjson props_json -break:10
python3 bots/dump_core/qlever_dumps/props/bot.py

python3 bots/dump_core/qlever_dumps/props/bot.py -break:10 props_json

"""
import json
import re
import copy
import requests
import sys
from pathlib import Path
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent))

from props_qlever_bot import one_prop, get_date, get_all_props, get_props_status
from props_text import make_text

PROPS_JSON = "props_json" in sys.argv
OLD_FROM_JSON = "oldjson" in sys.argv
MAIN_FROM_JSON = "fromjson" in sys.argv
REVERSE_PROPS = "desc" in sys.argv

dump_dir = Path(__file__).parent / 'dumps'
dump_to_wikidata_dir = dump_dir / 'to_wikidata'
texts_dir = dump_dir / 'texts'
qids_dir = dump_dir / 'qids_by_prop'
# ---
dump_to_wikidata_dir.mkdir(parents=True, exist_ok=True)
texts_dir.mkdir(parents=True, exist_ok=True)
qids_dir.mkdir(parents=True, exist_ok=True)

qids_old_file = dump_dir / 'qids_old.json'
props_main_file = dump_dir / "props.json"
qids_olds = {}

if qids_old_file.exists():
    with open(qids_old_file, 'r', encoding='utf-8') as f:
        qids_olds = json.load(f)

breaks = {1: 5_000}

for arg in sys.argv:
    arg, _, value = arg.partition(':')
    # ---
    if arg == '-break' and value.isdigit():
        breaks[1] = int(value)
        print(f"BREAK AT {value}\n" * 3)


def print_with_color(text, color):
    color_table = {
        "green": 32,
        "yellow": 33,
        "red": 31
    }
    # ---
    color_m = color_table.get(color, 0)
    # ---
    print(f"\033[{color_m}m{text}\033[0m")


def GetPageText_new(title):
    title = title.replace(' ', '_')
    # ---
    url = f'https://wikidata.org/wiki/{title}?action=raw'
    # ---
    print(f"url: {url}")
    # ---
    text = ''
    # ---
    session = requests.session()
    session.headers.update({"User-Agent": "Himo bot/1.0 (https://himo.toolforge.org/; tools.himo@toolforge.org)"})
    # ---
    # get url text
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad responses
        text = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page text: {e}")
        return ''
    # ---
    if not text:
        print(f'no text for {title}')
    # ---
    return text


def get_old_data(title):
    # ---
    texts = GetPageText_new(title)
    # ---
    try:
        Old = json.loads(texts)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        Old = {}
    # ---
    return Old


def get_old_props():
    # ---
    old_claims_file = dump_dir / "claims_old.json"
    # ---
    if OLD_FROM_JSON and old_claims_file.exists():
        # ---
        with open(old_claims_file, "r", encoding="utf-8") as f:
            old_claims = json.load(f)
        # ---
        if old_claims:
            return old_claims
    # ---
    old_data = get_old_data("User:Mr._Ibrahem/claims.json")
    # ---
    if old_data:
        with open(old_claims_file, "w", encoding="utf-8") as f:
            json.dump(old_data, f, ensure_ascii=False, indent=4)
    # ---
    return old_data


def get_props():
    itemsprop = get_all_props()
    # ---
    most_props_text = GetPageText_new("Template:Number of main statements by property")
    # ---
    properties = []
    # ---
    for line in most_props_text.split("\n"):
        match = re.match(r"\|(\d+)=(\d+)", line)
        if match:
            _, t2 = match.groups()
            properties.append(f"P{t2}")

    # Filter properties to include only those that are WikibaseItem types
    properties = [x for x in properties if x in itemsprop]
    # ---
    return properties[:101]


def get_prop_infos(p, p_old, n):
    # ---
    print_with_color(f"def get_prop_infos: {p}", "green")
    # ---
    file = qids_dir / f"{p}.json"
    # ---
    p_data = {}
    first_100 = {}
    # ---
    if file.exists():
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # ----
        first_100 = data.get("qids", {})
        # ----
        if PROPS_JSON:
            p_data = data
    # ---
    if n < breaks[1]:
        if not p_data or not p_data.get("qids_others"):
            p_data = one_prop(p, first_100=first_100)
    # ---
    if not p_data:
        return {}
    # ---
    prop_infos = {
        "property_claims_count": p_data.get("property_claims_count", 0),
        "unique_qids_count": p_data.get("unique_qids_count", 0),
        "items_with_property": p_data.get("items_with_property", 0),

        "qids_others": p_data["others"],
        "others": p_data["others"],

        "old": p_old,
        "qids": p_data["qids"],
    }
    # ---
    with open(file, "w", encoding="utf-8") as f:
        json.dump(prop_infos, f, ensure_ascii=False, indent=4)
    # ---
    if not p_old.get("qids", {}):
        p_old["qids"] = qids_olds.get(p, {})
    # ---
    prop_infos["old"] = p_old
    # ---
    return prop_infos


def props_ren(old_data):
    # ---
    # props = get_props()
    # ---
    old_properties = old_data.get("properties", {})
    # ---
    data = {
        "properties": {}
    }
    # ---
    # sort old_properties by p['property_claims_count']
    old_properties = dict(sorted(old_properties.items(), key=lambda item: item[1].get("property_claims_count", 0), reverse=REVERSE_PROPS))
    # ---
    for n, (p, p_old) in tqdm(enumerate(old_properties.items()), desc="Work on props:", total=len(old_properties)):
        # ---
        p_data = get_prop_infos(p, p_old, n)
        # ---
        if p_data:
            data["properties"][p] = p_data
    # ---
    return data


def load_data_main():
    # ---
    if not props_main_file.exists():
        return {}
    # ---
    data_main = {}
    # ---
    with open(props_main_file, "r", encoding="utf-8") as f:
        data_main = json.load(f)
    # ---
    if data_main:
        changed = False
        # ---
        for p, p_data in data_main["properties"].items():
            if not p_data.get("old", {}).get("qids", {}):
                data_main["properties"][p]["old"]["qids"] = qids_olds.get(p, {})
                # changed = True
        # ---
        if changed:
            with open(props_main_file, "w", encoding="utf-8") as f:
                json.dump(data_main, f, ensure_ascii=False, indent=4)
    # ---
    return data_main


def props_new_data(old_data, file_date):
    # ---
    data_main = {}
    # ---
    if MAIN_FROM_JSON:
        data_main = load_data_main()
    # ---
    if not data_main:
        # ---
        props_data = props_ren(old_data)
        # ---
        new_data = get_props_status()
        # ---
        all_items = new_data["all_items"]
        # ---
        data_main = {
            "date": file_date,
            "all_items": all_items,
            "old" : {x: v for x, v in old_data.items() if x != "properties"},
            "properties": props_data["properties"]
        }
    # ---
    data_dump = copy.deepcopy(data_main)
    # ---
    for p_data in data_dump["properties"].values():
        if "qids" in p_data:
            del p_data["qids"]
        if "qids" in p_data.get("old", {}):
            del p_data["old"]["qids"]
    # ---
    with open(props_main_file, "w", encoding="utf-8") as f:
        json.dump(data_dump, f, indent=4)
        print(f"save data_dump {len(data_dump)} to {str(props_main_file)}")
    # ---
    return data_main


def one_prop_tab(f):
    # ---
    result = {x: v for x, v in f.items() if x != "old"}
    # ---
    result["qids_others"] = f["qids_others"]
    result["qids"] = f["qids"]
    # ---
    return result


def render(old_data, file_date):
    # ---
    props_data = props_new_data(old_data, file_date)
    # ---
    all_items = props_data["all_items"]
    # ---
    to_save_data = {
        "date": file_date,
        "all_items": all_items,
        "items_missing_P31": 0,
        "items_with_0_claims": 0,
        "items_with_1_claim": 0,
        "total_claims_count": 0,
        "total_properties_count": 0,
        "properties": {
            "P31": {
                "items_with_property": 0,
                "property_claims_count": 0,
                "unique_qids_count": 0
            }
        }
    }
    # ---
    for p, p_data in props_data["properties"].items():
        if not p_data.get("old", {}).get("qids", {}):
            p_data["old"]["qids"] = qids_olds.get(p, {})
    # ---
    to_save_data.update({x: v for x, v in props_data.items() if x not in ["properties", "old"]})
    # ---
    properties = {
        x: one_prop_tab(f) for x, f
        in props_data["properties"].items()
    }
    # ---
    # sort properties by p['property_claims_count']
    properties = dict(sorted(properties.items(), key=lambda item: item[1].get("property_claims_count", 0), reverse=True))
    # ---
    to_save_data["properties"] = properties
    # ---
    file2 = dump_to_wikidata_dir / "properties.json"
    # ---
    with open(file2, "w", encoding="utf-8") as f:
        json.dump(to_save_data, f, indent=4)
        print(f"save {len(to_save_data)} to {str(file2)}")
    # ---
    text_file = texts_dir / "properties.txt"
    # ---
    text = make_text(props_data, props_data.get("old", {}))
    # ---
    with open(text_file, "w", encoding="utf-8") as outfile:
        outfile.write(text)
        print(f"save text to {str(text_file)}")


def main():
    # ---
    old_data = get_old_props()
    # ---
    file_date = get_date()
    file_date_old = old_data.get("file_date") or old_data.get("date")
    # ---
    if file_date == file_date_old:
        print(f"same old date {file_date=}")
        return
    else:
        print(f"new date {file_date=}")
    # ---
    render(old_data, file_date)


if __name__ == "__main__":
    main()
