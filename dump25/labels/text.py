#!/usr/bin/env python3
"""
python3 dump/labels/text.py
python3 text.py

"""
import sys
import json
import time
from pathlib import Path

# ---
va_dir = Path(__file__).parent
# ---
items_file = va_dir / "labels.json"
# ---
labels_file = va_dir / "labels.txt"
template_file = va_dir / "template.txt"
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


def facts(n_tab, Old):
    # ---
    last_total = Old.get("last_total", 0)
    # ---
    text = '{| class="wikitable sortable"\n'
    text += "! Title !! Id !! Number \n"
    # ---
    diff = n_tab["All_items"] - last_total
    # ---
    text += f"|-\n| Total items last update ||  || {last_total:,}\n"
    text += f"|-\n| Total items ||  || {n_tab['All_items']:,} (+{diff:,}) \n"
    # ---
    tats = ["labels", "descriptions", "aliases"]
    # ---
    tab_no = n_tab.get("no", {})
    if tab_no:
        for x in tats:
            text += f"|-\n| Items without {x} ||  || {tab_no[x]:,}\n"
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


def mainar(n_tab):
    start = time.time()

    with open(va_dir / "old_data.json", "r", encoding="utf-8") as f:
        Old = json.load(f)

    dumpdate = n_tab.get("file_date") or "latest"
    langs_table = n_tab["langs"]

    langs = sorted(langs_table.keys())

    last_total = Old.get("last_total", 0)

    rows = []

    test_new_descs = 0

    for code in langs:
        new_labels = 0
        new_descs = 0
        new_aliases = 0
        Old[code] = Old.get(code, {})
        _labels_ = langs_table[code].get("labels", 0)
        _descriptions_ = langs_table[code].get("descriptions", 0)
        _aliases_ = langs_table[code].get("aliases", 0)

        if code in Old:
            new_labels = _labels_ - Old[code].get("labels", 0)
            new_descs = _descriptions_ - Old[code].get("descriptions", 0)
            new_aliases = _aliases_ - Old[code].get("aliases", 0)
        else:
            print(f'code "{code}" not in Old')
        if new_descs != 0:
            test_new_descs = 1

        langs_tag_line = "{{#language:%s|en}}" % code
        langs_tag_line_2 = "{{#language:%s}}" % code
        # ---
        line = f"""| {code} || {langs_tag_line} || {langs_tag_line_2}\n"""
        # ---

        plus = "" if new_labels < 0 else "+"
        color_l = "#c79d9d" if new_labels < 0 else "#9dc79d" if new_labels > 0 else ""
        color_tag_l = "" if not color_l else f'style="background-color:{color_l}"|'
        # ---
        labels_co = make_cou(_labels_, n_tab["All_items"])
        line += f"""| {_labels_:,} || {labels_co} || {color_tag_l} {plus}{new_labels:,} """
        # ---

        d_plus = "" if new_descs < 0 else "+"
        color = "#c79d9d" if new_descs < 0 else "#9dc79d" if new_descs > 0 else ""
        color_tag = "" if not color else f'style="background-color:{color}"|'
        # ---
        descs_co = make_cou(_descriptions_, n_tab["All_items"])
        line += f"""|| {_descriptions_:,} || {descs_co} || {color_tag} {d_plus}{new_descs:,} """
        # ---

        a_plus = "" if new_aliases < 0 else "+"
        color_a = "#c79d9d" if new_aliases < 0 else "#9dc79d" if new_aliases > 0 else ""
        color_tag_a = "" if not color_a else f'style="background-color:{color_a}"|'
        # ---
        line += f"""|| {_aliases_:,} || {color_tag_a} {a_plus}{new_aliases:,}"""
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
    if test_new_descs == 0 and "test1" not in sys.argv:
        print("nothing new.. ")
        return ""
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

    if not text:
        return

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


if __name__ == "__main__":
    with open(items_file, "r", encoding="utf-8") as fa:
        tabb = json.load(fa)
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
