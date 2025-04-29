"""

python dump1/claims_max/text.py
python I:\core\bots\dump_core\dump26\claims_max\text.py

"""
import requests
import sys
import tqdm
import time
import json
from pathlib import Path

va_dir = Path(__file__).parent
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


def check_dir(path):
    if not path.exists():
        path.mkdir()


results_dir = Path(__file__).parent / "results"
check_dir(results_dir)

texts_tab = {}

sections_done = {"current": 0, "max": 100}

new_data_file = results_dir / "claims_max_data.json"
claims_max = results_dir / "claims_max.txt"
claims_p31 = results_dir / "claims_p31.txt"


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
    text += f"|-\n| Total items last update || {last_total:,} || 0 \n"
    # ---
    for key, title in texts.items():
        diff = min_it(n_tab[key], Old.get(key, 0), add_plus=True)
        text += f"|-\n| {title} || {n_tab[key]:,} || {diff} \n"
    # ---
    text += "|}\n\n"
    # ---
    return text


def pid_section_facts(table, old_data):
    # ---
    table["items_use_it"] = table.get("items_use_it") or table.get("lenth_of_usage", 0)
    old_data["items_use_it"] = old_data.get("items_use_it") or old_data.get("lenth_of_usage", 0)
    # ---
    text = '{| class="wikitable sortable"\n'
    text += "! Title !! Number !! Diff \n"
    # ---
    texts_tab_x = {
        "items_use_it": "Total items using this property",
        "len_prop_claims": "Total number of claims with this property:",
        "len_of_qids": "Number of unique QIDs",
    }
    # ---
    for key, title in texts_tab_x.items():
        diff = min_it(table[key], old_data.get(key, 0), add_plus=True)
        text += f"|-\n| {title} || {table[key]:,} || {diff} \n"
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


def make_section(pid, table, old_data, max_n=51):
    # ---
    qids_file = Path(__file__).parent / f"pids_qids/{pid}.json"
    # ---
    print(f"file:{qids_file}")
    # ---
    if not qids_file.exists():
        print(f"file not found: {qids_file}")
        return ""
    # ---
    if sections_done["current"] >= sections_done["max"]:
        texts_tab[pid] = ""
        return ""
    # ---
    old_data_qids = old_data.get("qids") or {"others": 0}
    # ---
    with open(qids_file, "r", encoding="utf-8") as file:
        qids = json.load(file)
        table["qids"] = fix_others(pid, qids)
    # ---
    new_data_qids = table.get("qids") or {"others": 0}
    # ---
    new_data["properties"][pid] = {
        "items_use_it": table.get("items_use_it", 0),
        # "lenth_of_usage": table.get("lenth_of_usage", 0),
        "len_prop_claims": table.get("len_prop_claims", 0),
        "len_of_qids": table.get("len_of_qids", 0),
        "qids": new_data_qids
    }
    # ---
    table_rows = []
    # ---
    sorted_qids = dict(sorted(new_data_qids.items(), key=lambda item: item[1], reverse=True))
    # ---
    for idx, (qid, count) in enumerate(sorted_qids.items(), start=1):
        if qid == "others":
            continue
        # ---
        old_v = old_data_qids.get(qid, 0)
        diffo = min_it(count, old_v, add_plus=True)
        # ---
        table_rows.append(f"! {idx} \n| {{{{Q|{qid}}}}} \n| {count:,} \n| {diffo}")
    # ---
    other_count = table["qids"].get("others", 0)
    # ---
    old_others = old_data_qids.get("others", 0)
    diff_others = min_it(other_count, old_others, add_plus=True)
    # ---
    table_rows.append(f"! {idx} \n! others \n! {other_count:,} \n! {diff_others} \n|-")
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


def make_numbers_section(p_list, Old):
    rows = []
    # ---
    Old_props = Old.get("properties", {})
    # ---
    other_count = 0
    # ---
    max_v = 500
    idx = 0
    # ---
    for idx, (usage, prop) in enumerate(p_list, start=1):
        # ---
        if len(rows) < max_v:
            old_prop = Old_props.get(prop, {})
            # ---
            old_usage = old_prop.get("items_use_it") or old_prop.get("lenth_of_usage", 0)
            # ---
            # print(f"{prop=}, {usage=}, {old_usage=}")
            # ---
            diff = min_it(usage, old_usage, add_plus=True)
            # ---
            # Unique_QIDs = data["properties"].get(prop, {}).get("len_of_qids", 0)
            # diff2 = min_it(Unique_QIDs, old_prop.get("len_of_qids", 0), add_plus=True)
            # ---
            # rows.append(f"| {idx} || {{{{P|{prop}}}}} || {Unique_QIDs:,}  || {diff2} || {usage:,} || {diff}")
            # ---
            rows.append(f"| {idx} || {{{{P|{prop}}}}} ||  {usage:,} || {diff}")
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
    rows.append(f"! {idx+1} \n! others || {other_count:,} || {o_diff}")
    # ---
    table_content = "\n|-\n".join(rows)
    # ---
    texts = "== Numbers ==\n"
    # ---
    table = f'{{| class="wikitable sortable"\n|-\n! # !! Property !! Items use it !! Diff\n|-\n{table_content}\n|}}\n'
    # ---
    texts += table
    # ---
    return texts


def make_text(data, Old):
    p_list = [(prop_data.get("items_use_it", prop_data.get("lenth_of_usage", 0)), prop_id) for prop_id, prop_data in data["properties"].items() if prop_data.get("items_use_it", prop_data.get("lenth_of_usage", 0))]
    p_list.sort(reverse=True)
    # ---
    print(f"{len(p_list)=}")
    # ---
    if not data.get("file_date"):
        data["file_date"] = "latest"
    # ---
    metadata = f"<onlyinclude>;dump date {data.get('file_date', 'latest')}</onlyinclude>.\n"
    metadata += facts(data, Old)
    # ---
    Old_props = Old.get("properties", {})
    # ---
    numbers_section = make_numbers_section(p_list, Old)

    sections = ""

    for _, prop in tqdm.tqdm(p_list, desc="def make_section(): "):
        sections += make_section(prop, data["properties"][prop], Old_props.get(prop, {}))

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
    title = "User:Mr._Ibrahem/claims.json"
    # ---
    if "old" in sys.argv:
        with open(Path(__file__).parent / "old.json", "r", encoding="utf-8") as file:
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
        with open(Path(__file__).parent / "old.json", "w", encoding="utf-8") as file:
            json.dump(Old, file, indent=4)
        # ---
        print("Old saved to old.json")
    # ---
    return Old


def get_split_tab():
    split_file = Path(__file__).parent / "split_tab.json"
    with open(split_file, "r", encoding="utf-8") as file:
        split_tab = json.load(file)

    data_defaults = {
        "delta": 0,
        "done": 0,
        "len_all_props": 0,
        "items_0_claims": 0,
        "items_1_claims": 0,
        "items_no_P31": 0,
        "All_items": 0,
        "total_claims": 0,
        "properties": {},
        "langs": {},
    }

    for key, default_value in data_defaults.items():
        if key not in split_tab:
            split_tab[key] = default_value

    for pid, tab in split_tab["properties"].copy().items():
        # ---
        items_use_it = tab.get("items_use_it") or tab.get("lenth_of_usage", 0)
        # ---
        split_tab["properties"][pid]["items_use_it"] = items_use_it
    # ---
    qids_dir = Path(__file__).parent / "pids_qids"
    # ---
    json_files = [x.name.replace(".json", "") for x in qids_dir.glob("*.json")]
    # ---
    split_tab["properties"] = {x: v for x, v in split_tab["properties"].items() if x in json_files}
    # ---
    print(f"len of split_tab properties: {len(split_tab['properties'])}")
    # ---
    return split_tab


def main():
    # ---
    time_start = time.time()
    print(f"time_start: {time_start}")
    # ---
    Old = get_old_data()
    # ---
    split_tab = get_split_tab()
    # ---
    text_output = make_text(split_tab, Old)
    # ---
    with open(claims_max, "w", encoding="utf-8") as file:
        file.write(text_output)
    # ---
    print(f"Log written to {claims_max}")
    # ---
    if "P31" in texts_tab:
        # ---
        with open(claims_p31, "w", encoding="utf-8") as file:
            file.write(texts_tab["P31"])
        # ---
        print(f"Log written to {claims_p31}")
    # ---
    with open(new_data_file, "w", encoding="utf-8") as outfile:
        json.dump(new_data, outfile, indent=4)
    # ---
    print(f"saved to {new_data_file}")


if __name__ == "__main__":
    main()
