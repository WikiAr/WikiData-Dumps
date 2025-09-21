"""

python3 core8/pwb.py I:/core/bots/wd_dumps/qlever_dumps/sitelinks/bot.py

"""
import json
import requests
import sys
from pathlib import Path
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent))

from texts_sites import make_text
from qlever_sites import get_sitelinks_data

new_codes = {
    # "bho": "",
    "gsw": "als",
    "egl": "eml",
    "nb": "no",
    "en-simple": "simple",

    "vro": "fiu-vro",

    "zh-classical": "lzh",
    "zh-min-nan": "nan",

    "zh-yue": "yue",
    "sgs": "bat-smg",

    "be-tarask": "",
    "cbk-x-zam": "",
    "crh-Latn": "",
    "fr-x-nrm": "",
    "it-x-tara": "",
    "jv-x-bms": "",
    "nds-NL": "",
    "rup": "",
}


def get_new(new_data, sitelinks_old):
    # ---
    new_dump_to_save = {
        "wikisource": {},
        "wikiquote": {},
        "wiktionary": {},
        "wikivoyage": {},
        "wikinews": {},
        "wikibooks": {},
        "wikiversity": {},
        "wikipedia": {},
        "others": {},
    }
    new_dump = {}
    # ---
    bad_codes = {}
    # ---
    for family, wikis in tqdm(new_data.items(), desc="Work on sitelinks:", total=len(new_data)):
        # ---
        new_dump_to_save.setdefault(family, {})
        new_dump.setdefault(family, {})
        # ---
        family_old = sitelinks_old.get(family, {})
        # ---
        for wiki, new_count in wikis.items():
            # ---
            old_value = family_old.get(wiki, 0)
            # ---
            wiki_new = new_codes.get(wiki) if new_codes.get(wiki) else wiki
            # ---
            if not old_value and wiki_new != wiki:
                old_value = family_old.get(wiki_new, 0)
            # ---
            new_dump_to_save[family][wiki_new] = new_count
            # ---
            if not old_value:
                bad_codes[wiki_new] = wiki
                # print(f"{wiki_new=} not in sitelinks_old, {wiki=}, {family=}")
            # ---
            new_dump[family][wiki_new] = {
                "new": new_count,
                "old": old_value,
            }
    # ---
    return new_dump_to_save, new_dump, bad_codes


def start(old_data, sitelinks_data):
    # ---
    new_data = sitelinks_data["new_data"]
    all_items = sitelinks_data["all_items"]
    items_without_sitelinks = sitelinks_data["items_without_sitelinks"]
    file_date = sitelinks_data["file_date"]
    # ---
    sitelinks_old = old_data.get("sitelinks", {}) or old_data
    # ---
    # "all_items": 117232191, "items_without_sitelinks": 83745912,
    # ---
    old_to_up = {
        "all_items": old_data.get("all_items", 0),
        "items_without_sitelinks": old_data.get("items_without_sitelinks", 0),
    }
    # ---
    new_dump_to_save, new_dump, bad_codes = get_new(new_data, sitelinks_old)
    # ---
    data = {
        "old_data": {},
        "file_date": file_date,
        "all_items": all_items,
        "items_without_sitelinks": items_without_sitelinks,
        "sitelinks": new_dump,
    }
    # ---
    data["old_data"].update(old_to_up)
    # ---
    to_save = {
        "file_date": file_date,
        "all_items": all_items,
        "items_without_sitelinks": items_without_sitelinks,
        "sitelinks": new_dump_to_save
    }
    # ---
    return data, to_save, bad_codes


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


def render(old_data, sitelinks_data):
    # ---
    file_date = sitelinks_data["file_date"]
    file_date_old = old_data["file_date"]
    # ---
    if file_date == file_date_old:
        print(f"same old date {file_date=}")
        return
    # ---
    data, to_save, bad_codes = start(old_data, sitelinks_data)
    # ---
    for code_new, code in bad_codes.items():
        print(f"* bad codes: \t {{{{int:project-localized-name-{code_new}wiki}}}} \t {{{{int:project-localized-name-{code}wiki}}}}")
    # ---
    text = make_text(data)
    # ---
    dump_dir = Path(__file__).parent / 'dumps'
    dump_to_wikidata_dir = dump_dir / 'to_wikidata'
    texts_dir = dump_dir / 'texts'
    # ---
    dump_to_wikidata_dir.mkdir(parents=True, exist_ok=True)
    texts_dir.mkdir(parents=True, exist_ok=True)
    # ---
    sitelinks_file = texts_dir / "sitelinks.txt"
    # ---
    with open(sitelinks_file, "w", encoding="utf-8") as outfile:
        outfile.write(text)
    # ---
    with open(dump_to_wikidata_dir / "sitelinks.json", "w", encoding="utf-8") as f:
        json.dump(to_save, f, indent=4)


def main():
    # ---
    old_data = get_old_data("User:Mr._Ibrahem/sitelinks.json")
    # ---
    print(f"len of old_data: {len(old_data)}")
    # ---
    sitelinks_data = get_sitelinks_data()
    # ---
    file_date = sitelinks_data.get("file_date", "")
    file_date_old = old_data.get("file_date") or old_data.get("date")
    # ---
    if file_date == file_date_old:
        print(f"same old date {file_date=}")
        return
    else:
        print(f"new date {file_date=}")
    # ---
    file = Path(__file__).parent / "tests/texts_test/sitelinks_new.json"
    # ---
    with open(file, "w", encoding="utf-8") as f:
        json.dump(sitelinks_data["new_data"], f, indent=4)
    # ---
    render(old_data, sitelinks_data)


if __name__ == "__main__":
    main()
