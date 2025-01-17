import sys
import time
import json
from pathlib import Path

sections_done = {"current": 0, "max": 100}

time_start = time.time()
print(f"time_start: {time_start}")

items_file = Path(__file__).parent / "claims.json"
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


def make_section(property_id, table, max_n=51):
    if sections_done["current"] >= sections_done["max"]:
        return ""

    total_usage = table.get("lenth_of_usage", 0)
    texts = f"== {{{{P|{property_id}}}}} ==\n"
    texts += f"* Total items using this property: {total_usage:,}\n"

    if claims_count := table.get("len_prop_claims"):
        texts += f"* Total number of claims with this property: {claims_count:,}\n"

    if unique_qids := table.get("len_of_qids"):
        texts += f"* Number of unique QIDs:  {unique_qids:,}\n"

    if not table.get("qids"):
        print(f"{property_id} has no QIDs.")
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
            table_rows.append(f"! {idx} \n| {{{{Q|{qid}}}}} \n| {count:,}")
            x_values.append(qid)
            y_values.append(str(count))
        else:
            other_count += count

    table_rows.append(f"! {idx} \n! others \n! {other_count:,}\n|-")
    table_content = "\n|-\n".join(table_rows)

    chart = ""
    if "Chart" in sys.argv:
        chart = make_chart(x_values, y_values, chart_type=2)

    section_table = '\n{| class="wikitable sortable plainrowheaders"\n|-\n! class="sortable" | #\n! class="sortable" | value\n! class="sortable" | Numbers\n|-\n'

    section_table += table_content + "\n|}\n{{clear}}\n"

    sections_done["current"] += 1
    return texts + chart + section_table


def make_numbers_section(p31_list):
    rows = []
    x_values, y_values = [], []
    other_count = 0
    idx = 0
    for idx, (usage, prop) in enumerate(p31_list, start=1):
        if idx <= 26:
            x_values.append(prop)
            y_values.append(str(usage))
        else:
            other_count += usage

        if len(rows) < 100:
            rows.append(f"| {idx} || {{{{P|{prop}}}}} || {usage:,}")

    rows.append(f"! {idx} \n! others \n! {other_count:,}\n|-")
    table_content = "\n|-\n".join(rows)
    # ---
    texts = "== Numbers ==\n\n"
    # ---
    if "Chart" in sys.argv:
        chart = make_chart(x_values, y_values)
        texts += chart + "\n"
    # ---
    table = f'\n{{| class="wikitable sortable"\n|-\n! # !! Property !! Usage\n{table_content}\n|}}\n'
    # ---
    texts += table
    # ---
    return texts


def make_text(data):
    p31_list = [(prop_data["lenth_of_usage"], prop_id) for prop_id, prop_data in data["properties"].items() if prop_data["lenth_of_usage"]]
    p31_list.sort(reverse=True)

    if not data.get("file_date"):
        data["file_date"] = "latest"
    # ---
    metadata = f"<onlyinclude>;dump date {data.get('file_date', 'latest')}</onlyinclude>.\n"
    metadata += f"* Total items: {data['All_items']:,}\n"
    metadata += f"* Items without P31: {data['items_no_P31']:,}\n"
    metadata += f"* Items without claims: {data['items_0_claims']:,}\n"
    metadata += f"* Items with 1 claim only: {data['items_1_claims']:,}\n"
    metadata += f"* Total number of claims: {data['total_claims']:,}\n"
    metadata += f"* Number of properties in the report: {data['len_all_props']:,}\n"
    # ---
    final = time.time()
    delta = data.get("delta") or int(final - time_start)
    metadata += f"<!-- bots work done in {delta} secounds --> \n--~~~~~\n"
    chart_section = make_numbers_section(p31_list)

    sections = "".join(make_section(prop, data["properties"][prop]) for _, prop in p31_list if sections_done["current"] < sections_done["max"])

    return metadata + chart_section + sections


def main():
    with open(items_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    data_defaults = {
        "delta": 0,
        "done": 0,
        "len_all_props": len(data.get("properties", {})),
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

    text_output = make_text(data)

    with open(claims_new, "w", encoding="utf-8") as file:
        file.write(text_output)
    print(f"Log written to {claims_new}")

    if "P31" in data["properties"]:
        text_p31_output = make_section("P31", data["properties"]["P31"], max_n=501)
        with open(claims_p31, "w", encoding="utf-8") as file:
            file.write(text_p31_output)
        print(f"Log written to {claims_p31}")


if __name__ == "__main__":
    main()
