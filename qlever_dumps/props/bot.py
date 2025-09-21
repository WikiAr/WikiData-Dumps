"""

python3 core8/pwb.py I:/core/bots/dump_core/qlever_dumps/props/bot.py
python3 bots/dump_core/qlever_dumps/props/bot.py

"""
import json
import re
import requests
import sys
from pathlib import Path
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent))

from props_qlever_bot import one_prop, get_date, get_all_props, get_props_status
from props_text import make_text

dump_dir = Path(__file__).parent / 'dumps'
dump_to_wikidata_dir = dump_dir / 'to_wikidata'
texts_dir = dump_dir / 'texts'
qids_dir = dump_dir / 'qids_by_prop'
# ---
dump_to_wikidata_dir.mkdir(parents=True, exist_ok=True)
texts_dir.mkdir(parents=True, exist_ok=True)
qids_dir.mkdir(parents=True, exist_ok=True)


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
    if "fromjson" in sys.argv and old_claims_file.exists():
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
    for p, p_old in tqdm(old_properties.items(), desc="Work on props:", total=len(old_properties)):
        # ---
        p_data = one_prop(p)
        # ---
        data["properties"][p] = {
            "qids_others": p_data["others"],
            "others": p_data["others"],
            "new": p_data["new"],
            "old": p_old,
            "qids": p_data["qids"],
        }
        # ---
        file = qids_dir / f"{p}.json"
        # ---
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data["properties"][p], f, indent=4)
        # ---
        break
    # ---
    return data


def props_new_data(old_data, file_date):
    # ---
    if "fromjson" in sys.argv:
        # ---
        with open(dump_dir / "props.json", "r", encoding="utf-8") as f:
            props_data = json.load(f)
        # ---
        if props_data:
            return props_data
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
    file1 = dump_dir / "props.json"
    # ---
    with open(file1, "w", encoding="utf-8") as f:
        json.dump(data_main, f, indent=4)
        print(f"save data_main {len(data_main)} to {str(file1)}")
    # ---
    return data_main


def render(old_data, file_date):
    # ---
    props_data = props_new_data(old_data, file_date)
    # ---
    all_items = props_data["all_items"]
    # ---
    to_save_data = {
        "date": file_date,
        "all_items": all_items,
        "items_no_P31": 937647,
        "items_0_claims": 1482902,
        "items_1_claims": 8972766,
        "total_claims": 790665159,
        "len_all_props": 100,
        "properties": {
            "P31": {
                "items_use_it": 113220756,
                "len_prop_claims": 121322991,
                "len_of_qids": 105592
            }
        }
    }
    # ---
    to_save_data.update({x: v for x, v in props_data.items() if x not in ["properties", "old"]})
    # ---
    to_save_data["properties"] = {
        x: f["new"] for x, f
        in props_data["properties"].items()
        if f["new"]
    }
    # ---
    file2 = dump_to_wikidata_dir / "properties.json"
    # ---
    with open(file2, "w", encoding="utf-8") as f:
        json.dump(to_save_data, f, indent=4)
        print(f"save {len(to_save_data)} to {str(file2)}")
    # ---
    text_file = texts_dir / "properties.txt"
    # ---
    text = make_text(props_data)
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
