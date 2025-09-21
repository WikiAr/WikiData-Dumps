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

from qlever_bot import one_prop, one_lang, get_all_props

dump_dir = Path(__file__).parent / 'dumps'
qids_dir = dump_dir / 'qids_by_prop'

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


def props_render():
    # ---
    # props = get_props()
    # ---
    old_properties = get_old_data("User:Mr._Ibrahem/claims.json").get("properties", {})
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
    with open(dump_dir / "props.json", "w", encoding="utf-8") as f:
        json.dump(prop_data_dump, f, indent=4)
    # ---
    return prop_data_dump


def lang_render():
    # ---
    old_langs = get_old_data("User:Mr._Ibrahem/langs.json")
    old_langs_items = old_langs.get("langs", {})
    # ---
    lang_data = {}
    # ---
    for lang, old_data in tqdm(old_langs_items.items(), desc="Work on langs:", total=len(old_langs_items)):
        # ---
        p_data = one_lang(lang)
        # ---
        lang_data[lang] = {
            "new": p_data,
            "old": old_data
        }
    # ---
    data = {
        "old": {
            "all_items": old_langs.get("last_total") or old_langs.get("all_items"),
            "without": old_langs.get("without"),
        },
        "langs": lang_data
    }
    # ---
    with open(dump_dir / "langs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    # ---
    return lang_data


if __name__ == "__main__":
    if "props" in sys.argv:
        props_render()
    elif "langs" in sys.argv:
        lang_render()
