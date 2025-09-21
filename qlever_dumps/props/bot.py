"""

python3 core8/pwb.py I:/core/bots/wd_dumps/qlever_dumps/new/start.py langs
python3 core8/pwb.py I:/core/bots/wd_dumps/qlever_dumps/new/start.py props
python3 new_dump/start.py

"""
import json
import re
import requests
import sys
from pathlib import Path
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent))

from qlever_bot import one_prop, get_date, get_all_props

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
    prop_data_dump = {}
    # ---
    for p, p_old in tqdm(old_properties.items(), desc="Work on props:", total=len(old_properties)):
        # ---
        p_data = one_prop(p)
        # ---
        prop_data_dump[p] = {
            "new": p_data["new"],
            "old": p_old
        }
        # ---
        p_data["old"] = p_old
        # ---
        file = qids_dir / f"{p}.json"
        # ---
        with open(file, "w", encoding="utf-8") as f:
            json.dump(p_data, f, indent=4)
    # ---
    return prop_data_dump


def render(old_data, file_date):
    # ---
    props_data = props_ren(old_data)
    # ---
    if "fromjson" in sys.argv:
        all_items = props_data["all_items"]
        withouts = props_data["without"]
    else:
        # ---
        new_data = get_langs_status()
        # ---
        all_items = new_data["all_items"]
        withouts = new_data["without"]
        # ---
        data_new = {
            "date": file_date,
            "all_items": all_items,
            "without": withouts,
            "langs": props_data["langs"]
        }
        # ---
        with open(dump_dir / "props.json", "w", encoding="utf-8") as f:
            json.dump(data_new, f, indent=4)
        # ---
    # ---
    to_save_data = {
        "date": file_date,
        "all_items": all_items,
        "without": withouts,
    }
    # ---
    to_save_data["langs"] = {x: f["new"] for x, f in props_data["langs"].items() if f["new"]}
    # ---
    with open(dump_to_wikidata_dir / "langs.json", "w", encoding="utf-8") as f:
        json.dump(to_save_data, f, indent=4)
    # ---
    text_file = texts_dir / "langs.txt"
    temp_file = texts_dir / "template.txt"
    # ---
    text = make_text(props_data)
    temp_text = make_temp_text(props_data)
    # ---
    with open(temp_file, "w", encoding="utf-8") as outfile:
        outfile.write(temp_text)
    # ---
    with open(text_file, "w", encoding="utf-8") as outfile:
        outfile.write(text)


def main():
    # ---
    old_data = get_old_data("User:Mr._Ibrahem/claims.json")
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
