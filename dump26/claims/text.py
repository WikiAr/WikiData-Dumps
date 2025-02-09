"""

python3 dump/claims/text2.py

python3 /data/project/himo/bots/dump_core/dump25/claims/text2.py


"""
import requests
import sys
import time
import json
from pathlib import Path

va_dir = Path(__file__).parent
# ---
new_data_file = Path(__file__).parent / "claims_new_data.json"
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

sections_done = {"current": 0, "max": 100}

time_start = time.time()
print(f"time_start: {time_start}")

items_file = Path(__file__).parent / "claims.json"

if "P31" in sys.argv:
    items_file = Path(__file__).parent / "claims_P31.json"

claims_new = Path(__file__).parent / "claims_new.txt"
claims_p31 = Path(__file__).parent / "claims_p31.txt"


def make_chart(x_values, y_values, chart_type=1):
    if not x_values or not y_values:
        return ""

    x_line = ",".join(x_values)
    y_line = ",".join(y_values)
    chart = '{| class="floatright sortable"\n|-\n|\n'
    chart += "{{Graph:Chart"

    if chart_type == 1:
        chart += "|width=900|height=100|xAxisTitle=property|yAxisTitle=usage|type=rect\n"
    else:
        chart += "|width=140|height=140|xAxisTitle=value|yAxisTitle=Number|legend=value\n"
        chart += "|type=pie|showValues1=offset:8,angle:45\n"

    chart += f"|x={x_line}\n|y1={y_line}\n"
    chart += "}}\n|}\n"
    chart = chart.replace("=,", "=")
    return chart


def make_section(pid, table, old_data, max_n=51):
    # ---
    if sections_done["current"] >= sections_done["max"]:
        return ""
    # ---
    new_data["properties"][pid] = {
        "items_use_it": 0,
        "lenth_of_usage": 0,
        "len_prop_claims": 0,
        "len_of_qids": 0,
        "qids": {
            "others": 0,
        },
    }
    # ---
    total_usage = table.get("items_use_it", table.get("lenth_of_usage", 0))
    # ---
    old_usage = old_data.get("items_use_it", old_data.get("lenth_of_usage", 0))
    # ---
    claims_count = 0
    unique_qids = table.get("len_of_qids", 0)
    # ---
    if not table.get("qids"):
        print(f"{pid} has no QIDs.")
        return ""

    table_rows = []
    x_values, y_values = [], []
    other_count = 0

    sorted_qids = dict(sorted(table["qids"].items(), key=lambda item: item[1], reverse=True))
    idx = 0
    for idx, (qid, count) in enumerate(sorted_qids.items(), start=1):
        if qid == "others":
            other_count += count
            continue

        # if idx <= max_n:
        if idx < max_n:
            old_v = old_data.get("qids", {}).get(qid, 0)
            diffo = min_it(count, old_v, add_plus=True)
            # ---
            table_rows.append(f"! {idx} \n| {{{{Q|{qid}}}}} \n| {count:,} \n| {diffo}")
            # ---
            new_data["properties"][pid]["qids"][qid] = count
            claims_count += count
            # ---
            x_values.append(qid)
            y_values.append(str(count))
        else:
            other_count += count
    # ---
    claims_count += other_count
    # ---
    new_data["properties"][pid]["qids"]["others"] = other_count
    # ---
    old_others = old_data.get("qids", {}).get("others", 0)
    diff_others = min_it(other_count, old_others, add_plus=True)
    # ---
    table_rows.append(f"! {idx} \n! others \n! {other_count:,} \n! {diff_others} \n|-")
    # ---
    table_content = "\n|-\n".join(table_rows)

    chart = ""

    if "Chart" in sys.argv:
        chart = make_chart(x_values, y_values, chart_type=2)

    texts = f"== {{{{P|{pid}}}}} ==\n"
    # --- -
    diff = min_it(total_usage, old_usage, add_plus=True)
    # ---
    texts += f"* Total items using this property: {total_usage:,} ({diff})\n"

    if claims_count:
        diff2 = min_it(claims_count, old_data.get("len_prop_claims", 0), add_plus=True)
        texts += f"* Total number of claims with this property: {claims_count:,} ({diff2})\n"

    if unique_qids:
        diff3 = min_it(unique_qids, old_data.get("len_of_qids", 0), add_plus=True)
        texts += f"* Number of unique QIDs: {unique_qids:,} ({diff3})\n"

    new_data["properties"][pid]["lenth_of_usage"] = total_usage
    new_data["properties"][pid]["items_use_it"] = total_usage
    # ---
    new_data["properties"][pid]["len_prop_claims"] = claims_count
    new_data["properties"][pid]["len_of_qids"] = unique_qids

    section_table = '\n{| class="wikitable sortable plainrowheaders"\n|-'
    section_table += '\n! class="sortable" | #'
    section_table += '\n! class="sortable" | value'
    section_table += '\n! class="sortable" | Numbers'
    section_table += '\n! class="sortable" | Diff'
    section_table += '\n|-\n'

    section_table += table_content + "\n|}\n{{clear}}\n"

    sections_done["current"] += 1
    return texts + chart + section_table


def make_numbers_section(p_list, Old_props):
    rows = []
    x_values, y_values = [], []
    other_count = 0
    idx = 0

    max_v = 100 if "P31" not in sys.argv else 501

    for idx, (usage, prop) in enumerate(p_list, start=1):
        if idx <= 26:
            x_values.append(prop)
            y_values.append(str(usage))
        else:
            other_count += usage

        if len(rows) < max_v:
            old_prop = Old_props.get(prop, {})
            old_usage = old_prop.get("items_use_it") or old_prop.get("lenth_of_usage", 0)
            diff = min_it(usage, old_usage, add_plus=True)
            rows.append(f"| {idx} || {{{{P|{prop}}}}} || {usage:,} || {diff}")

    rows.append(f"! {idx} \n! others \n! {other_count:,}\n|-")
    table_content = "\n|-\n".join(rows)
    # ---
    texts = "== Numbers ==\n\n"
    # ---
    if "Chart" in sys.argv:
        chart = make_chart(x_values, y_values)
        texts += chart + "\n"
    # ---
    table = f'\n{{| class="wikitable sortable"\n|-\n! # !! Property !! Usage !! Diff\n{table_content}\n|}}\n'
    # ---
    texts += table
    # ---
    return texts


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
        new_data[key] = int(n_tab[key])
    # ---
    text += "|}\n\n"
    # ---
    return text


def make_text(data, Old):
    p_list = [(prop_data.get("items_use_it", prop_data.get("lenth_of_usage", 0)), prop_id) for prop_id, prop_data in data["properties"].items() if prop_data.get("items_use_it", prop_data.get("lenth_of_usage", 0))]
    p_list.sort(reverse=True)

    if not data.get("file_date"):
        data["file_date"] = "latest"
    # ---
    metadata = f"<onlyinclude>;dump date {data.get('file_date', 'latest')}</onlyinclude>.\n"
    metadata += facts(data, Old)
    # ---
    Old_props = Old.get("properties", {})
    # ---
    final = time.time()
    delta = data.get("delta") or int(final - time_start)
    metadata += f"<!-- bots work done in {delta} secounds --> \n--~~~~\n"
    chart_section = make_numbers_section(p_list, Old_props)

    sections = ""

    for _, prop in p_list:
        if sections_done["current"] < sections_done["max"]:
            sections += make_section(prop, data["properties"][prop], Old_props.get(prop, {}))

    return metadata + chart_section + sections


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
    texts = GetPageText_new(title)
    # ---
    try:
        Old = json.loads(texts)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        Old = {}
    # ---
    return Old


def main():
    with open(items_file, "r", encoding="utf-8") as file:
        data = json.load(file)

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
        data.setdefault(key, default_value)

    Old = get_old_data()

    text_output = make_text(data, Old)

    with open(claims_new, "w", encoding="utf-8") as file:
        file.write(text_output)

    print(f"Log written to {claims_new}")

    if "P31" in data["properties"]:
        text_p31_output = make_section("P31", data["properties"]["P31"], Old.get("properties", {}).get("P31", {}), max_n=501)
        with open(claims_p31, "w", encoding="utf-8") as file:
            file.write(text_p31_output)
        print(f"Log written to {claims_p31}")

    with open(new_data_file, "w", encoding="utf-8") as outfile:
        json.dump(new_data, outfile, indent=4)

    print(f"saved to {new_data_file}")


if __name__ == "__main__":
    main()
