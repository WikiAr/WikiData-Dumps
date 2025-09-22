"""

python3 core8/pwb.py I:/core/bots/wd_dumps/qlever_dumps/langs/bot.py fromjson
python3 core8/pwb.py I:/core/bots/wd_dumps/qlever_dumps/langs/bot.py

"""
import json
import requests
import sys
from pathlib import Path
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent))

from qlever_bot import one_lang, get_date, get_langs_status
from langs_text import make_text, make_temp_text

dump_dir = Path(__file__).parent / 'dumps'
dump_to_wikidata_dir = dump_dir / 'to_wikidata'
texts_dir = dump_dir / 'texts'
# ---
dump_to_wikidata_dir.mkdir(parents=True, exist_ok=True)
texts_dir.mkdir(parents=True, exist_ok=True)


def GetPageText_new(title):
    # ---
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


def lang_ren(old_langs):
    # ---
    old_langs_items = old_langs.get("langs", {})
    # ---
    data = {
        "langs": {}
    }
    # ---
    if "fromjson" in sys.argv:
        with open(dump_dir / "langs.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    # ---
    else:
        for lang, old_data in tqdm(old_langs_items.items(), desc="Work on langs:", total=len(old_langs_items)):
            # ---
            p_data = one_lang(lang)
            # ---
            data["langs"][lang] = {
                "new": p_data,
                "old": old_data
            }
    # ---
    data["old"] = {
        "all_items": old_langs.get("last_total") or old_langs.get("all_items"),
        "without": old_langs.get("without"),
    }
    # ---
    return data


def render(old_data, file_date):
    # ---
    lang_data = lang_ren(old_data)
    # ---
    if "fromjson" in sys.argv:
        all_items = lang_data["all_items"]
        withouts = lang_data["without"]
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
            "langs": lang_data["langs"]
        }
        # ---
        file1 = dump_dir / "langs.json"
        # ---
        with open(file1, "w", encoding="utf-8") as f:
            json.dump(data_new, f, indent=4)
            print(f"save {len(data_new)} to {str(file1)}")
    # ---
    to_save_data = {
        "date": file_date,
        "all_items": all_items,
        "without": withouts,
    }
    # ---
    to_save_data["langs"] = {x: f["new"] for x, f in lang_data["langs"].items() if f["new"]}
    # ---
    file2 = dump_to_wikidata_dir / "langs.json"
    # ---
    with open(file2, "w", encoding="utf-8") as f:
        json.dump(to_save_data, f, indent=4)
        print(f"save {len(to_save_data)} to {str(file2)}")
    # ---
    text_file = texts_dir / "langs.txt"
    temp_file = texts_dir / "template.txt"
    # ---
    text = make_text(lang_data)
    temp_text = make_temp_text(lang_data)
    # ---
    with open(temp_file, "w", encoding="utf-8") as outfile:
        outfile.write(temp_text)
        print(f"save temp_text to {str(temp_file)}")
    # ---
    with open(text_file, "w", encoding="utf-8") as outfile:
        outfile.write(text)
        print(f"save text to {str(text_file)}")
    # ---


def main():
    # ---
    old_langs = get_old_data("User:Mr._Ibrahem/langs.json")
    # ---
    file_date = get_date()
    file_date_old = old_langs.get("file_date") or old_langs.get("date")
    # ---
    if file_date == file_date_old:
        print(f"same old date {file_date=}")
        return
    else:
        print(f"new date {file_date=}")
    # ---
    render(old_langs, file_date)


if __name__ == "__main__":
    main()
