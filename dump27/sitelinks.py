#!/usr/bin/env python3
"""
python3 dump/sitelinks/text.py

python3 dump25/sitelinks/text.py

"""
import sys
import os
import requests
import re
import json
from datetime import datetime
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent))

from dir_handler import sitelinks_results_dir, labels_results_dir

items_file = labels_results_dir / "labels_new.json"
# ---
new_data = {
    "date": "",
    "last_total": 0,
    "items_without_sitelinks": 0,
    "sitelinks": {},
}
# ---
new_data_file = sitelinks_results_dir / "sitelinks.json"
labels_file = sitelinks_results_dir / "sitelinks.txt"
# ---
main_table_head = """
== sitelinks per family ==
"""
families_names = {
    "others": "{{int:wikibase-sitelinks-special}}",
    "wikisource": "{{int:Wikibase-otherprojects-wikisource}}",
    "wikipedia": "{{int:Wikibase-otherprojects-wikipedia}}",
    "wikiquote": "{{int:Wikibase-otherprojects-wikiquote}}",
    "wiktionary": "{{int:Wikibase-otherprojects-wiktionary}}",
    "wikibooks": "{{int:Wikibase-otherprojects-wikibooks}}",
    "wikinews": "{{int:Wikibase-otherprojects-wikinews}}",
    "wikiversity": "{{int:Wikibase-otherprojects-wikiversity}}",
    "wikivoyage": "{{int:Wikibase-otherprojects-wikivoyage}}",
}


def make_name(code):
    # ---
    names = {
        "wikidatawiki": "{{int:Wikibase-otherprojects-wikidata}}",
        "commonswiki": "{{int:Wikibase-otherprojects-commons}}",
        "specieswiki": "{{int:Wikibase-otherprojects-species}}",
        "metawiki": "{{int:Project-localized-name-metawiki}}",
        "mediawikiwiki": "{{int:Project-localized-name-mediawikiwiki}}",
        "wikimaniawiki": "{{int:Project-localized-name-wikimaniawiki}}",
    }
    # ---
    lab = f"{{{{int:project-localized-name-{code}}}}}"
    # ---
    return lab
    # return names.get(code, lab)


def make_link(code, family):
    links = {
        "wikimaniawiki": "[[:wikimania:|wikimaniawiki]]",
        "metawiki": "[[:m:|metawiki]]",
        "mediawikiwiki": "[[:mw:|mediawikiwiki]]",
        "wikidatawiki": "[[d:|wikidatawiki]]",
        "wikifunctionswiki": "[[:wikifunctions:|wikifunctionswiki]]",
        "specieswiki": "[[:species:|specieswiki]]",
        "sourceswiki": "",
        "outreachwiki": "[[:outreachwiki:|outreachwiki]]",
        "foundationwiki": "[[:foundation:|foundationwiki]]",
        "commonswiki": "[[:c:|commonswiki]]",
    }
    # ---
    link = links.get(code, "")
    # ---
    if link:
        return link
    # ---
    if family == "wikipedia":
        co = code.replace("wiki", "")
        link = f"[[:w:{co}:|{code}]]"
        return link
    # ---
    families_links = {
        "wikisource": "[[:s:{}:|{}]]",
        "wikipedia": "[[:w:{}:|{}]]",
        "wikiquote": "[[:q:{}:|{}]]",
        "wiktionary": "[[:wikt:{}:|{}]]",
        "wikibooks": "[[:b:{}:|{}]]",
        "wikinews": "[[:n:{}:|{}]]",
        "wikiversity": "[[:v:{}:|{}]]",
        "wikivoyage": "[[:voy:{}:|{}]]",
    }
    # ---
    if family in families_links:
        co = re.sub(rf"{family}$", "", code)
        link = families_links[family].format(co, code)
        return link
    # ---
    if link == "":
        return code
    # ---
    return link


def split_by_family(tab):
    # ---
    new = {}
    # ---
    familys = [
        "wikisource",
        "wikiquote",
        "wiktionary",
        "wikivoyage",
        "wikinews",
        "wikibooks",
        "wikiversity",
        # "wiki",
    ]
    # ---
    others = [
        "metawiki",
        "mediawikiwiki",
        "wikidatawiki",
        "wikifunctionswiki",
        "wikimaniawiki",
        "specieswiki",
        "sourceswiki",
        "outreachwiki",
        "foundationwiki",
        "commonswiki",
    ]
    # ---
    for family in familys:
        new[family] = {x: v for x, v in tab.items() if x.endswith(family)}
    # ---
    new["wikipedia"] = {x: v for x, v in tab.items() if not any(x.endswith(y) for y in familys) and x not in others}
    new["others"] = {x: v for x, v in tab.items() if x in others}
    # ---
    with open(sitelinks_results_dir / "splits.json", "w", encoding="utf-8") as f:
        json.dump(new, f)
    # ---
    return new


def make_cou(num, _all):
    if num == 0 or _all == 0:
        return "0%"
    # ---
    fef = (num / _all) * 100
    # ---
    st = f"{str(fef)[:4]}%"
    # ---
    if st == "0.00%":
        st = "0%"
    # ---
    return st


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


def make_families_text_u(du_tab, Old, All_items):
    text_tab = {}
    # ---
    old_sitelinks = Old.get("sitelinks", {})
    # ---
    for family, sitelinks in du_tab.items():
        # ---
        family_rows = []
        # ---
        n = 0
        # ---
        all_links = sum(sitelinks.values())
        # ---
        for code, _sitelinks_ in sitelinks.items():
            new_data["sitelinks"][code] = _sitelinks_
            n += 1
            new_sitelinks = 0
            new_sitelinks = min_it(_sitelinks_, old_sitelinks.get(code, 0))

            # langs_tag_line = "{{#language:%s|en}}" % code
            # langs_tag_line_2 = "{{#language:%s}}" % code
            # line = f"""| {code} || {langs_tag_line} || {langs_tag_line_2}\n"""
            # ---
            plus = "" if new_sitelinks < 1 else "+"
            color_l = "#c79d9d" if new_sitelinks < 0 else "#9dc79d" if new_sitelinks > 0 else ""
            color_tag_l = "" if not color_l else f'style="background-color:{color_l}"|'
            # ---
            # labels_co = make_cou(_sitelinks_, All_items)
            # ---
            wikilink = make_link(code, family)
            # ---
            wikiname = make_name(code)
            # ---
            # line = f"""| {wikilink} || {wikiname} || {_sitelinks_:,} || {labels_co} || {color_tag_l} {plus}{new_sitelinks:,} """
            line = f"""| {n} || {wikilink} || {wikiname} || {_sitelinks_:,} || {color_tag_l} {plus}{new_sitelinks:,} """
            # ---
            family_rows.append(line)
        # ---
        family_name = family
        # ---
        if families_names.get(family, family) != family:
            family_name = family + " / " + families_names.get(family, family)
        # ---
        if family == "others":
            family_section = f"== {family_name} ==\n"
        else:
            family_section = f"=== {family_name} ===\n"
        # ---
        # family
        # ---
        family_section += f"* Total number of links: {all_links:,}\n"
        # ---
        family_section += '{| class="wikitable sortable"\n'
        # family_section += "! Code !! Name !! Number of links !! % !! New \n|-\n"
        family_section += "! # !! Code !! Name !! Number of links !! New \n|-\n"
        # ---
        family_section += "\n|-\n".join(family_rows)
        # ---
        family_section += "\n|}\n"
        # ---
        text_tab[family] = family_section
    # ---
    return text_tab


def make_families_text(du_tab, Old, All_items):
    text = ""
    # ---
    families_text = make_families_text_u(du_tab, Old, All_items)
    # ---
    sort_list = [
        "others",
        "wikipedia",
        "wiktionary",
        "wikibooks",
        "wikinews",
        "wikiquote",
        "wikisource",
        "wikiversity",
        "wikivoyage",
    ]
    # ---
    # sort families_text keys by sort_list or but it in the last
    families_text = dict(sorted(families_text.items(), key=lambda x: sort_list.index(x[0]) if x[0] in sort_list else len(sort_list) + 1))
    # ---
    others_txt = families_text.get("others", "")
    # ---
    text += f"{others_txt}\n"
    # ---
    del families_text["others"]
    # ---
    text += main_table_head
    # ---
    text += "\n\n".join(families_text.values())
    # ---
    return text


def facts(n_tab, Old):
    # ---
    last_total = Old.get("last_total", 0)
    # ---
    text = '{| class="wikitable sortable"\n'
    text += "! Title !! Number !! Diff \n"
    # ---
    # diff = n_tab["All_items"] - int(last_total)
    diff = min_it(n_tab["All_items"], last_total, add_plus=True)
    # ---
    text += f"|-\n| Total items last update || {last_total:,} || 0 \n"
    text += f"|-\n| Total items || {n_tab['All_items']:,}  || {diff} \n"
    # ---
    no_sitelinks = n_tab.get("no", {}).get("sitelinks", 0)
    # ---
    new_data["items_without_sitelinks"] = no_sitelinks
    # ---
    no_sitelinks_diff = min_it(no_sitelinks, Old.get("items_without_sitelinks", 0), add_plus=True)
    # ---
    text += f"|-\n| Items without sitelinks || {no_sitelinks:,} || {no_sitelinks_diff} \n"
    # ---
    if n_tab.get("most", {}).get("sitelinks"):
        q = n_tab["most"]["sitelinks"]["q"]
        count = n_tab["most"]["sitelinks"]["count"]
        text += f"|-\n| Most linked item ([[{q}]]) || {count:,} || \n"
    # ---
    text += "|}\n\n"
    # ---
    return text


def GetPageText_new(title):
    title = title.replace(' ', '_')
    # ---
    url = f'https://wikidata.org/wiki/{title}?action=raw'
    # ---
    print(f"url: {url}")
    # ---
    text = ''
    # ---
    # get url text
    try:
        response = requests.get(url, timeout=10)
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
    title = "User:Mr._Ibrahem/sitelinks.json"
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


def mainar(n_tab):
    Old = get_old_data()
    # ---
    dumpdate = n_tab.get("file_date") or "latest"
    du_tab = n_tab["sitelinks"]

    last_total = Old.get("last_total", 0)

    du_tab = split_by_family(du_tab)

    diff = n_tab["All_items"] - int(last_total)
    # ---
    new_data["last_total"] = n_tab["All_items"]
    # ---
    text = f"Update: <onlyinclude>{dumpdate}</onlyinclude>.\n"
    text += "--~~~~\n\n"
    # ---
    text += facts(n_tab, Old)
    # ---
    families_text = make_families_text(du_tab, Old, n_tab["All_items"])
    # ---
    text += families_text
    # ---
    text += "\n[[Category:Wikidata statistics|Sitelinks]]"
    # ---
    print(f"Total items last update: {last_total:,}")
    print(f"Total items new: {n_tab['All_items']:,}")
    print(f"diff: {diff:,}")
    # ---
    return text


def main_labels(tabb):
    # ---
    text = mainar(tabb)
    # ---
    text = text.replace("[[Category:Wikidata statistics|sitelinks statistics]]", "")
    # ---
    with open(labels_file, "w", encoding="utf-8") as outfile:
        outfile.write(text)
    # ---
    print(f"saved to {labels_file}")
    # ---
    # sort new_data['sitelinks'] by keys
    new_data["sitelinks"] = dict(sorted(new_data["sitelinks"].items()))
    # ---
    with open(new_data_file, "w", encoding="utf-8") as outfile:
        json.dump(new_data, outfile, indent=4)
    # ---
    print(f"saved to {new_data_file}")


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


def main():
    with open(items_file, "r", encoding="utf-8") as fa:
        tabb = json.load(fa)
    # ---
    new_data["date"] = check_date()
    # ---
    tab = {
        "delta": 0,
        "done": 0,
        "file_date": "",
        "All_items": 0,
        "sitelinks": {},
    }
    # ---
    for x, v in tab.items():
        if x not in tabb:
            tabb[x] = v
    # ---
    print(f"Total items: {tab['All_items']:,}")
    # ---
    main_labels(tabb)


if __name__ == "__main__":
    main()
