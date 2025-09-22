#!/usr/bin/env python3
"""
python3 dump/labels/text.py
python3 text.py

"""
import sys
import requests
import os
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dir_handler import labels_results_dir

new_data_file = labels_results_dir / "labels_new_data.json"
items_file = labels_results_dir / "labels_new.json"
labels_file = labels_results_dir / "labels.txt"
template_file = labels_results_dir / "template.txt"
# ---
new_data = {
    "date": "",
    "last_total": 0,
    "without": {
        "labels": 0,
        "descriptions": 0,
        "aliases": 0,
    },
    "langs": {},
}
# ---
main_table_head = """
== Number of labels, descriptions and aliases for items per language ==
{| class="wikitable sortable"
! rowspan="2" |Language code
! colspan="2" |Language
! colspan="3" data-sort-type="number" |Labels
! colspan="3" data-sort-type="number" |Descriptions
! colspan="2" data-sort-type="number" |Aliases
|-
!English !!Native !!All !! % !!New !!All !! % !!New !!All !!New
|-
"""


def wiki_link(title):
    return f"[[{title}]]" if title else ""


def make_cou(num, _all):
    if num == 0 or _all == 0:
        return "0%"
    fef = (num / _all) * 100
    return f"{str(fef)[:4]}%"


def min_it(new, old, add_plus=False):
    old = str(old)
    # ---
    if old.isdigit():
        old = int(old)
    else:
        return 0
    # ---
    result = new - old
    # ---
    if add_plus:
        plus = "" if result < 1 else "+"
        result = f"{plus}{result:,}"
    # ---
    return result


def facts(n_tab, Old):
    # ---
    last_total = Old.get("last_total", 0)
    # ---
    text = '{| class="wikitable sortable"\n'
    text += "! Title !! Number !! Diff \n"
    # ---
    # diff = n_tab["All_items"] - last_total
    diff = min_it(n_tab["All_items"], last_total, add_plus=True)
    # ---
    new_data["last_total"] = int(n_tab["All_items"])
    # ---
    text += f"|-\n| Total items last update || {last_total:,} || 0 \n"
    text += f"|-\n| Total items || {n_tab['All_items']:,} || {diff} \n"
    # ---
    tats = ["labels", "descriptions", "aliases"]
    # ---
    old_without = Old.get("without", {})
    # ---
    tab_no = n_tab.get("no", {})
    if tab_no:
        for x in tats:
            new_data["without"][x] = int(tab_no[x])
            # ---
            old_v = old_without.get(x, 0)
            # ---
            diff_v = min_it(tab_no[x], old_v, add_plus=True)
            # ---
            text += f"|-\n| Items without {x} || {tab_no[x]:,} || {diff_v} \n"
    # ---
    text += "|}\n\n"
    # ---
    text += '{| class="wikitable sortable"\n'
    text += "! Title !! Id !! Number \n"
    # ---
    tab_most = n_tab.get("most", {})
    if tab_most:
        for x in tats:
            if tab_most[x]["q"]:
                text += f"|-\n| Item with most {x} || {wiki_link(tab_most[x]['q'])} || {tab_most[x]['count']:,}\n"
    # ---
    text += "|}\n\n"
    # ---
    return text


def get_color_style(value: int) -> tuple[str, str]:
    """Return color and plus/minus prefix based on value."""
    plus = "" if value < 0 else "+"
    color = "#c79d9d" if value < 0 else "#9dc79d" if value > 0 else ""
    tag = "" if not color else f'style="background-color:{color}"|'
    # ---
    return tag, plus


def format_language_line(code, langs_table, old_values, n_tab):
    langs_tag_line = f"{{{{#language:{code}|en}}}}"
    langs_tag_line_2 = f"{{{{#language:{code}}}}}"

    labels = langs_table[code].get("labels", 0)
    descriptions = langs_table[code].get("descriptions", 0)
    aliases = langs_table[code].get("aliases", 0)
    # ---
    new_data["langs"][code] = {
        "labels": labels,
        "descriptions": descriptions,
        "aliases": aliases,
    }
    # ---
    new_labels = labels - old_values.get("labels", 0)
    new_descs = descriptions - old_values.get("descriptions", 0)
    new_aliases = aliases - old_values.get("aliases", 0)

    color_tag_l, plus = get_color_style(new_labels)
    color_tag_d, d_plus = get_color_style(new_descs)
    color_tag_a, a_plus = get_color_style(new_aliases)

    labels_co = make_cou(labels, n_tab["All_items"])
    descs_co = make_cou(descriptions, n_tab["All_items"])

    line = f"| {code} || {langs_tag_line} || {langs_tag_line_2}\n"
    line += f"| {labels:,} || {labels_co} || {color_tag_l} {plus}{new_labels:,} "
    line += f"|| {descriptions:,} || {descs_co} || {color_tag_d} {d_plus}{new_descs:,} "
    line += f"|| {aliases:,} || {color_tag_a} {a_plus}{new_aliases:,}"
    return line


def format_language_line_new(code, langs_table, old_values, n_tab):
    langs_tag_line = f"{{{{#language:{code}|en}}}}"
    langs_tag_line_2 = f"{{{{#language:{code}}}}}"

    fields = ["labels", "descriptions", "aliases"]
    # ---
    line = f"| {code} || {langs_tag_line} || {langs_tag_line_2} "
    # ---
    new_data["langs"][code] = {
        "labels": langs_table[code].get("labels", 0),
        "descriptions": langs_table[code].get("descriptions", 0),
        "aliases": langs_table[code].get("aliases", 0),
    }
    # ---
    for field in fields:
        all = langs_table[code].get(field, 0)
        new = all - old_values.get(field, 0)

        color_tag_l, plus = get_color_style(new)

        if field == "aliases":
            line += f"|| {all:,} || {color_tag_l} {plus}{new:,} "
        else:
            num_co = make_cou(all, n_tab["All_items"])
            line += f"|| {all:,} || {num_co} || {color_tag_l} {plus}{new:,} "
    # ---
    return line


def mainar(n_tab):
    start = time.time()

    Old = get_old_data()

    dumpdate = n_tab.get("file_date") or "latest"
    langs_table = n_tab["langs"]

    langs = sorted(langs_table.keys())

    last_total = Old.get("last_total", 0)

    rows = []

    langs_old = Old.get("langs", {})

    for code in langs:
        # ---
        if code not in langs_old:
            print(f'code "{code}" not in Old')
        # ---
        old_values = langs_old.get(code, {})
        # ---
        line = format_language_line(code, langs_table, old_values, n_tab)
        # ---
        rows.append(line)
    # ---
    rows = "\n|-\n".join(rows)
    # ---
    table = main_table_head
    # ---
    table += rows
    # ---
    table += "\n|}\n[[Category:Wikidata statistics|Language statistics]]"
    # ---
    final = time.time()
    delta = n_tab.get("delta") or int(final - start)
    # ---
    diff = n_tab["All_items"] - last_total
    # ---
    print(f"Total items last update: {last_total:,}")
    print(f"Total items new: {n_tab['All_items']:,}")
    print(f"diff: {diff:,}")
    # ---
    text = f"Update: <onlyinclude>{dumpdate}</onlyinclude>.\n"
    text += "--~~~~\n"
    # ---
    text += facts(n_tab, Old)
    # ---
    text += f"<!-- bots work done in {delta} secounds --> \n"
    text = f"{text}\n{table}"
    # ---
    text = text.replace("0 (0000)", "0")
    text = text.replace("0 (0)", "0")
    # ---
    return text


def make_temp_text(ttab):
    langs_tab = ttab.get("langs", {})
    # ---
    tmp_text = "{{#switch:{{{c}}}"
    # ---
    # sort langs_tab by name
    langs_tab = dict(sorted(langs_tab.items()))
    # ---
    for x, tab in langs_tab.items():
        tmp_text += f"\n|{x}={str(tab['labels'])}"
    # ---
    tmp_text += "\n}}"
    # ---
    return tmp_text


def main_labels(tabb):
    # ---
    # from dump.labels.do_text import main_labels# main_labels(tabb)
    # ---
    text = mainar(tabb)
    # ---
    tmp_text = make_temp_text(tabb)
    # ---
    text = text.replace("[[Category:Wikidata statistics|Language statistics]]", "")
    # ---
    with open(labels_file, "w", encoding="utf-8") as outfile:
        outfile.write(text)
    # ---
    print(f"saved to {labels_file}")
    # ---
    with open(template_file, "w", encoding="utf-8") as outfile:
        outfile.write(tmp_text)
    # ---
    print(f"saved to {template_file}")
    # ---
    with open(new_data_file, "w", encoding="utf-8") as outfile:
        json.dump(new_data, outfile, indent=4)
    # ---
    print(f"saved to {new_data_file}")


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


def get_old_data():
    # ---
    title = "User:Mr._Ibrahem/langs.json"
    # ---
    texts = GetPageText_new(title)
    # ---
    try:
        Old = json.loads(texts)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        Old = {}
    # ---
    if not Old:
        old_file = Path(__file__).parent / "old.json"
        if old_file.exists():
            with open(old_file, "r", encoding="utf-8") as infile:
                Old = json.load(infile)
    # ---
    return Old


def check_date():
    bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
    # get last change time of bz2_file
    try:
        last_change = os.path.getmtime(bz2_file)
        # ---
        return datetime.fromtimestamp(last_change).strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error: {e}")
        return ""


if __name__ == "__main__":
    with open(items_file, "r", encoding="utf-8") as fa:
        tabb = json.load(fa)
    # ---
    new_data["date"] = check_date()
    # ---
    tab = {
        "no": {
            "labels": 0,
            "descriptions": 0,
            "aliases": 0,
        },
        "most": {
            "labels": {"q": "", "count": 0},
            "descriptions": {"q": "", "count": 0},
            "aliases": {"q": "", "count": 0},
        },
        "delta": 0,
        "done": 0,
        "file_date": "",
        "All_items": 0,
        "langs": {},
    }
    # ---
    for x, v in tab.items():
        if x not in tabb:
            tabb[x] = v
    # ---
    main_labels(tabb)
