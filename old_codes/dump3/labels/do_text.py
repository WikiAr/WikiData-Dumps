#!/usr/bin/env python3
"""

python3 core8/pwb.py dump3/labels/do_text
python3 core8/pwb.py dump3/labels/do_text test
python3 core8/pwb.py dump3/labels/do_text test nosave

"""
import sys
import codecs
import json
import time
from pathlib import Path

# ---
try:
    from dump3.labels.labels_old_values import make_old_values  # make_old_values()
except ImportError:
    from labels_old_values import make_old_values  # make_old_values()
# ---
do_test = "test" in sys.argv
# ---
va_dir = Path(__file__).parent.parent
texts_dir = va_dir / "texts"
# ---
items_file = va_dir / "jsons/items.json"
# ---
labels_file = va_dir / "texts/labels.txt"
template_file = va_dir / "texts/template.txt"
# ---
if do_test:
    texts_dir = va_dir / "texts_test"
    items_file = va_dir / "jsons/items_test.json"
# ---
labels_file = texts_dir / "labels.txt"
template_file = texts_dir / "template.txt"
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


def make_cou(num, _all):
    if num == 0 or _all == 0:
        return "0%"
    fef = (num / _all) * 100
    return f"{str(fef)[:4]}%"


def mainar(n_tab):
    start = time.time()

    Old = make_old_values()

    dumpdate = n_tab.get('file_date') or 'latest'
    langs_table = n_tab['langs']

    langs = sorted(langs_table.keys())

    last_total = Old.get('last_total', 0)

    rows = []

    test_new_descs = 0

    for code in langs:
        new_labels = 0
        new_descs = 0
        new_aliases = 0

        _labels_ = langs_table[code]['labels']
        _descriptions_ = langs_table[code]['descriptions']
        _aliases_ = langs_table[code]['aliases']

        if code in Old:
            new_labels = _labels_ - Old[code]['labels']
            new_descs = _descriptions_ - Old[code]['descriptions']
            new_aliases = _aliases_ - Old[code]['aliases']
        else:
            print(f'code "{code}" not in Old')
        if new_descs != 0:
            test_new_descs = 1

        langs_tag_line = "{{#language:%s|en}}" % code
        langs_tag_line_2 = "{{#language:%s}}" % code
        # ---
        line = f'''| {code} || {langs_tag_line} || {langs_tag_line_2}\n'''
        # ---

        plus = '' if new_labels < 0 else '+'
        color_l = "#c79d9d" if new_labels < 0 else "#9dc79d" if new_labels > 0 else ""
        color_tag_l = '' if not color_l else f'style="background-color:{color_l}"|'
        # ---
        labels_co = make_cou(_labels_, n_tab['All_items'])
        line += f'''| {_labels_:,} || {labels_co} || {color_tag_l} {plus}{new_labels:,} '''
        # ---

        d_plus = '' if new_descs < 0 else '+'
        color = "#c79d9d" if new_descs < 0 else "#9dc79d" if new_descs > 0 else ""
        color_tag = '' if not color else f'style="background-color:{color}"|'
        # ---
        descs_co = make_cou(_descriptions_, n_tab['All_items'])
        line += f'''|| {_descriptions_:,} || {descs_co} || {color_tag} {d_plus}{new_descs:,} '''
        # ---

        a_plus = '' if new_aliases < 0 else '+'
        color_a = "#c79d9d" if new_aliases < 0 else "#9dc79d" if new_aliases > 0 else ""
        color_tag_a = '' if not color_a else f'style="background-color:{color_a}"|'
        # ---
        line += f'''|| {_aliases_:,} || {color_tag_a} {a_plus}{new_aliases:,}'''
        # ---

        rows.append(line)
    # ---
    rows = '\n|-\n'.join(rows)
    # ---
    table = main_table_head
    # ---
    table += rows
    # ---
    table += "\n|}\n[[Category:Wikidata statistics|Language statistics]]"
    # ---
    if test_new_descs == 0 and 'test1' not in sys.argv:
        print('nothing new.. ')
        return ''
    # ---
    final = time.time()
    delta = n_tab.get('delta') or int(final - start)
    # ---
    diff = n_tab['All_items'] - last_total
    # ---
    print(f'Total items last update: {last_total:,}')
    print(f"Total items new: {n_tab['All_items']:,}")
    print(f"diff: {diff:,}")
    # ---
    text = f"Update: <onlyinclude>{dumpdate}</onlyinclude>.\n"
    text += f"* Total items last update:{last_total:,}.\n"
    text += f"* Total items:{n_tab['All_items']:,}. (+{diff})\n"
    text += f"<!-- bots work done in {delta} secounds --> \n"
    text += "--~~~~~\n"
    text = f"{text}\n{table}"
    text = text.replace("0 (0000)", "0")
    text = text.replace("0 (0)", "0")

    if not text:
        return

    return text


def make_temp_text(ttab):
    langs_tab = ttab.get('langs', {})
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
    if "nosave" in sys.argv:
        return
    # ---
    text = text.replace('[[Category:Wikidata statistics|Language statistics]]', '')
    # ---
    with open(labels_file, "w", encoding="utf-8") as outfile:
        outfile.write(text)
    # ---
    print(f'saved to {labels_file}')
    # ---
    with open(template_file, "w", encoding="utf-8") as outfile:
        outfile.write(tmp_text)
    # ---
    print(f'saved to {template_file}')


if __name__ == '__main__':
    with open(items_file, "r", encoding="utf-8") as fa:
        tabb = json.load(fa)
    # ---
    main_labels(tabb)
