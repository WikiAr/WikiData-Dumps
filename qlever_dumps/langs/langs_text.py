#!/usr/bin/env python3
"""
"""
import time
from pathlib import Path

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
    all_items_old = Old.get("all_items", 0)
    all_items_new = n_tab.get("all_items", 0)
    # ---
    text = '{| class="wikitable sortable"\n'
    text += "! Title !! Number !! Diff \n"
    # ---
    diff = min_it(all_items_new, all_items_old, add_plus=True)
    # ---
    text += f"|-\n| Total items last update || {all_items_old:,} || 0 \n"
    text += f"|-\n| Total items || {all_items_new:,} || {diff} \n"
    # ---
    tats = ["labels", "descriptions", "aliases"]
    # ---
    old_without = Old.get("without", {})
    # ---
    tab_no = n_tab.get("without", {})
    # ---
    if tab_no:
        for x in tats:
            # ---
            old_v = int(old_without.get(x, 0))
            # ---
            cur_v = int(tab_no.get(x, 0))
            # ---
            diff_v = min_it(cur_v, old_v, add_plus=True)
            # ---
            text += f"|-\n| Items without {x} || {cur_v:,} || {diff_v} \n"
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


def format_language_line(code, new_values, old_values, n_tab):
    langs_tag_line = f"{{{{#language:{code}|en}}}}"
    langs_tag_line_2 = f"{{{{#language:{code}}}}}"

    labels = new_values.get("labels", 0)
    descriptions = new_values.get("descriptions", 0)
    aliases = new_values.get("aliases", 0)
    # ---
    new_labels = labels - old_values.get("labels", 0)
    new_descs = descriptions - old_values.get("descriptions", 0)
    new_aliases = aliases - old_values.get("aliases", 0)

    color_tag_l, plus = get_color_style(new_labels)
    color_tag_d, d_plus = get_color_style(new_descs)
    color_tag_a, a_plus = get_color_style(new_aliases)

    labels_co = make_cou(labels, n_tab.get("all_items", 0))
    descs_co = make_cou(descriptions, n_tab.get("all_items", 0))

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
    for field in fields:
        all_a = langs_table[code].get(field, 0)
        new = all_a - old_values.get(field, 0)

        color_tag_l, plus = get_color_style(new)

        if field == "aliases":
            line += f"|| {all_a:,} || {color_tag_l} {plus}{new:,} "
        else:
            num_co = make_cou(all_a, n_tab.get("all_items", 0))
            line += f"|| {all_a:,} || {num_co} || {color_tag_l} {plus}{new:,} "
    # ---
    return line


def make_text(n_tab):
    start = time.time()

    Old = n_tab.get("old", {})

    dumpdate = n_tab.get("date") or "latest"
    langs_table = n_tab["langs"]

    # sort langs_table by keys
    langs_table = {key: langs_table[key] for key in sorted(langs_table)}

    all_items_old = Old.get("all_items", 0)

    rows = []

    for code, tab in langs_table.items():
        # ---
        line = format_language_line(code, tab["new"], tab["old"], n_tab)
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
    diff = n_tab.get("all_items", 0) - all_items_old
    # ---
    print(f"Total items last update: {all_items_old:,}")
    print(f"Total items new: {n_tab['all_items']:,}")
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
        tmp_text += f"\n|{x}={str(tab['new']['labels'])}"
    # ---
    tmp_text += "\n}}"
    # ---
    return tmp_text
