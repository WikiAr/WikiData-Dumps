"""

python dump1/claims_max/text.py
python I:/core/bots/dump_core/dump26/claims_max/text.py

"""
import requests
import sys
import tqdm
import time
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dir_handler import pids_qids_dir, most_props_path, claims_results_dir, dump_files_dir

# ---
new_data = {
    "date": "",
    "All_items": 0,
    "items_no_P31": 0,
    "items_0_claims": 0,
    "items_1_claims": 0,
    "total_claims": 0,
    "len_all_props": 0,
    "properties": {},
}

most_props = json.loads(most_props_path.read_text())

texts_tab = {}

sections_done = {"current": 0, "max": 100}

new_data_file = claims_results_dir / "claims_max_data.json"
claims_max = claims_results_dir / "claims_max.txt"
claims_p31 = claims_results_dir / "claims_p31.txt"


def min_it(new, old, add_plus=False):
    old = str(old)
    # ---
    if old.isdigit():
        old = int(old)
    else:
        return 0
    # ---
    if old == 0 or new == old:
        return 0
    # ---
    result = new - old
    # ---
    if add_plus:
        plus = "" if result < 1 else "+"
        result = f"{plus}{result:,}"
    # ---
    return result


def min_it_tab(new_tab, old_tab, key, add_plus=False):
    # ---
    old = old_tab.get(key, 0)
    new = new_tab.get(key, 0)
    # ---
    return min_it(new, old, add_plus=add_plus)


def facts(n_tab, Old):
    # ---
    last_total = Old.get("All_items", 0)
    # ---
    text = '{| class="wikitable sortable"\n'
    text += "! Title !! Number !! Diff \n"
    # ---
    texts = {
        "All_items": "Total items",
        "items_no_P31": "Items without P31",
        "items_0_claims": "Items without claims",
        "items_1_claims": "Items with 1 claim only",
        "total_claims": "Total number of claims",
        "len_all_props": "Number of properties in the report",
    }
    # ---
    report_date = n_tab.get('file_date') or n_tab.get('date') or "latest"
    # ---
    text += f"|-\n| Report date || {report_date} ||  \n"
    text += f"|-\n| Total items last update || {last_total:,} ||  \n"
    # ---
    for key, title in texts.items():
        diff = min_it_tab(n_tab, Old, key, add_plus=True)
        # ---
        text += f"|-\n| {title} || {n_tab[key]:,} || {diff} \n"
    # ---
    text += "|}\n\n"
    # ---
    return text


def pid_section_facts(table, old_data):
    # ---
    table["items_use_it"] = table.get("items_use_it") or table.get("len_of_usage", 0)
    old_data["items_use_it"] = old_data.get("items_use_it") or old_data.get("len_of_usage", 0)
    # ---
    text = '{| class="wikitable sortable"\n'
    text += "! Title !! Number !! Diff \n"
    # ---
    texts_tab_x = {
        # "items_use_it": "Total items using this property",
        "len_prop_claims": "Total number of claims:",
        # "len_of_qids": "Number of unique QIDs",
    }
    # ---
    for key, title in texts_tab_x.items():
        # ---
        new_value = table.get(key, 0)
        # ---
        diff = min_it_tab(table, old_data, key, add_plus=True)
        # ---
        text += f"|-\n| {title} || {new_value:,} || {diff} \n"
    # ---
    text += "|}\n\n"
    # ---
    return text


def fix_others(pid, qids_tab, max=0):
    # ---
    max_items = 500 if pid == "P31" else 100
    max_items += 2
    # ---
    if max > 0 :
        max_items = max
    # ---
    if len(qids_tab.items()) > max_items:
        # ---
        others = qids_tab.get("others", 0)
        # ---
        print(f"len of qids: {len(qids_tab.items())}, others: {others}")
        # ---
        qids_tab["others"] = 0
        # ---
        if qids_tab.get("null", 0):
            qids_tab["others"] = qids_tab.get("null", 0)
            del qids_tab["null"]
        # ---
        qids_1 = sorted(qids_tab.items(), key=lambda x: x[1], reverse=True)
        # ---
        qids_tab = dict(qids_1[:max_items])
        # ---
        others += sum([x[1] for x in qids_1[max_items:]])
        # ---
        print(f" new others: {others}")
        # ---
        qids_tab["others"] = others
    # ---
    return qids_tab


def load_qids(pid, table):
    # ---
    qids_file = pids_qids_dir / f"{pid}.json"
    # ---
    print(f"file:{qids_file}")
    # ---
    if not qids_file.exists():
        print(f"file not found: {qids_file}")
        return {}
    # ---
    new_data["properties"][pid] = {
        "items_use_it": table.get("items_use_it", 0),
        # "len_of_usage": table.get("len_of_usage", 0),
        "len_prop_claims": table.get("len_prop_claims", 0),
        "len_of_qids": table.get("len_of_qids", 0),
        # "qids": new_data_qids
    }
    # ---
    new_qids = {}
    # ---
    with open(qids_file, "r", encoding="utf-8") as file:
        qids = json.load(file)
    # ---
    new_data["properties"][pid]["len_of_qids"] = len(qids.get("qids", {}))
    # ---
    new_qids = fix_others(pid, qids.get("qids", {}))
    # ---
    return new_qids


def make_section(pid, table, old_data, max_n=51):
    # ---
    if sections_done["current"] >= sections_done["max"]:
        texts_tab[pid] = ""
        return ""
    # ---
    old_data_qids = old_data.get("qids") or {"others": 0}
    # ---
    new_data_qids = table.get("qids") or {"others": 0}
    # ---
    table_rows = []
    # ---
    sorted_qids = dict(sorted(new_data_qids.items(), key=lambda item: item[1], reverse=True))
    # ---
    other_count = table["qids"].get("others", 0)
    # ---
    idx = 0
    # ---
    for idx, (qid, count) in enumerate(sorted_qids.items(), start=1):
        # ---
        if qid == "others":
            continue
        # ---
        old_v = old_data_qids.get(qid, 0)
        # ---
        diffo = min_it(count, old_v, add_plus=True)
        # ---
        table_rows.append(f"! {idx} \n| {{{{Q|{qid}}}}} \n| {count:,} \n| {diffo}")
    # ---
    old_others = old_data_qids.get("others", 0)
    diff_others = min_it(other_count, old_others, add_plus=True)
    # ---
    table_rows.append(f"! {idx+1} \n! others \n! {other_count:,} \n! - \n|-")
    # ---
    table_content = "\n|-\n".join(table_rows)
    # ---
    texts = f"== {{{{P|{pid}}}}} ==\n"
    # ---
    texts += pid_section_facts(table, old_data)
    # ---
    section_table = '\n{| class="wikitable sortable plainrowheaders"\n|-'
    section_table += '\n! class="sortable" | #'
    section_table += '\n! class="sortable" | value'
    section_table += '\n! class="sortable" | Numbers'
    section_table += '\n! class="sortable" | Diff'
    section_table += '\n|-\n'

    section_table += table_content + "\n|}\n{{clear}}\n"

    sections_done["current"] += 1
    # ---
    final_text = texts + section_table
    # ---
    texts_tab[pid] = final_text
    # ---
    del table
    # ---
    return final_text


def make_numbers_section(properties_infos, Old):
    # ---
    rows = []
    # ---
    Old_props = Old.get("properties", {})
    # ---
    other_count = 0
    # ---
    max_v = 500
    idx = 0
    # ---
    for idx, (prop, prop_tab) in enumerate(properties_infos.items(), start=1):
        # ---
        if len(rows) < max_v:
            # ---
            # usage = prop_tab.get("items_use_it", 0)
            usage = prop_tab.get("len_prop_claims", 0)
            # ---
            old_prop = Old_props.get(prop, {})
            # ---
            old_usage = old_prop.get("len_prop_claims")
            diff = min_it(usage, old_usage, add_plus=True)
            # ---
            value_in_most_props = most_props.get(prop, 0)
            # ---
            line = f"| {idx} || {{{{P|{prop}}}}} || {usage:,} <!-- {value_in_most_props:,} -->|| {diff}"
            # ---
            # len_prop_claims = prop_tab.get("len_prop_claims", 0)
            # diff2 = min_it_tab(prop_tab, old_prop, "len_prop_claims", add_plus=True)
            # # ---
            # line += f" || {len_prop_claims:,}  || {diff2}"
            # ---
            rows.append(line)
        else:
            other_count += usage
    # ---
    oo_others = Old.get("others", 0)
    # ---
    if not isinstance(oo_others, int):
        oo_others = 0
    # ---
    o_diff = min_it(other_count, oo_others, add_plus=True)
    # ---
    rows.append(f"! {idx+1} \n! others || {other_count:,} || -")
    # ---
    table_content = "\n|-\n".join(rows)
    # ---
    texts = "== Numbers ==\n"
    # ---
    table = '| class="wikitable sortable"\n|-\n'
    table += '! # !! Property'
    # table += '!! Items use it !! Diff'
    table += '!! Claims !! Diff'
    table += f'\n|-\n{table_content}\n'
    # ---
    table = f'{{{table}|}}\n'
    # ---
    texts += table
    # ---
    return texts


def make_text(data, Old):
    # ---
    properties_infos = dict(sorted(data["properties"].items(), key=lambda x: x[1].get("len_prop_claims", 0), reverse=True))
    # ---
    print(f"{len(properties_infos)=}")
    # ---
    # if not data.get("file_date"): data["file_date"] = "latest"
    # ---
    metadata = facts(data, Old)
    # ---
    metadata += "\n--~~~~\n\n"
    # ---
    Old_props = Old.get("properties", {})
    # ---
    numbers_section = make_numbers_section(properties_infos, Old)
    # ---
    sections = ""
    # ---
    section_done = 0
    # ---
    for prop, prop_tab in tqdm.tqdm(properties_infos.items(), desc="def make_section(): "):
        # ---
        prop_tab['qids'] = load_qids(prop, prop_tab)
        # ---
        if section_done < 11:
            sections += make_section(prop, prop_tab, Old_props.get(prop, {}))
            # ---
            section_done += 1
    # ---
    return metadata + numbers_section + sections


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
    title = "User:Mr._Ibrahem/claims.json"
    # ---
    if "old" in sys.argv:
        with open(claims_results_dir / "old_claims.json", "r", encoding="utf-8") as file:
            Old = json.load(file)
            return Old
    # ---
    texts = GetPageText_new(title)
    # ---
    try:
        Old = json.loads(texts)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        Old = {}
    # ---
    if Old:
        with open(claims_results_dir / "old_claims.json", "w", encoding="utf-8") as file:
            json.dump(Old, file, indent=4)
        # ---
        print("Old saved to old_claims.json")
    # ---
    return Old


def get_split_tab():
    split_file = dump_files_dir / "claims_stats.json"
    # ---
    # { "len_all_props": 0, "items_0_claims": 1482902, "items_1_claims": 8972766, "items_no_P31": 937647, "All_items": 115641305, "total_claims": 790665159 }
    with open(split_file, "r", encoding="utf-8") as file:
        claims_stats = json.load(file)
    # ---
    data_defaults = {
        "date": "",
        "All_items": 0,
        "items_no_P31": 0,
        "items_0_claims": 0,
        "items_1_claims": 0,
        "total_claims": 0,
        "len_all_props": 0,
        "properties": {},
    }
    # ---
    for key, default_value in data_defaults.items():
        if key not in claims_stats:
            claims_stats[key] = default_value
            print(f"set default value for {key}")
    # ---
    files = list(pids_qids_dir.glob("*.json"))
    # ---
    for file_path in tqdm.tqdm(files):
        pid = file_path.stem
        # ---
        with open(file_path, "r", encoding="utf-8") as file:
            pid_data = json.load(file)
        # ---
        if pid_data.get("qids"):
            del pid_data["qids"]
        # ---
        pid_data["items_use_it"] = pid_data.get("items_use_it") or pid_data.get("len_of_usage") or 0
        # ---
        claims_stats["properties"][pid] = pid_data
    # ---
    if not claims_stats.get("len_all_props"):
        claims_stats["len_all_props"] = len(claims_stats["properties"])
    # ---
    print(f"len of claims_stats properties: {len(claims_stats['properties'])}")
    # ---
    for x, numb in claims_stats.items():
        if isinstance(numb, int):
            print(f"claims_stats: {x} == {numb:,}")
    # ---
    return claims_stats


def main():
    # ---
    time_start = time.time()
    print(f"time_start: {time_start}")
    # ---
    Old = get_old_data()
    # ---
    claims_stats = get_split_tab()
    # ---
    text_output = make_text(claims_stats, Old)
    # ---
    with open(claims_max, "w", encoding="utf-8") as file:
        file.write(text_output)
    # ---
    print(f"Log written to {claims_max}")
    # ---
    if "P31" in texts_tab:
        # ---
        text = f"--~~~~\n\n{texts_tab['P31']}"
        # ---
        with open(claims_p31, "w", encoding="utf-8") as file:
            file.write(text)
        # ---
        print(f"Log written to {claims_p31}")
    # ---
    claims_stats["properties"] = new_data["properties"]
    # ---
    with open(new_data_file, "w", encoding="utf-8") as outfile:
        json.dump(claims_stats, outfile, indent=4)
    # ---
    print(f"saved to {new_data_file}")


if __name__ == "__main__":
    main()
