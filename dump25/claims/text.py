"""

python3 dump/claims/text.py

python3 /data/project/himo/bots/dump_core/dump25/claims/text.py


"""
import sys
import time
import json
from pathlib import Path

# ---
time_start = time.time()
print(f"time_start:{str(time_start)}")
# ---
items_file = Path(__file__).parent / "claims.json"
# ---
claims_new = Path(__file__).parent / "claims_new.txt"
claims_p31 = Path(__file__).parent / "claims_p31.txt"
# ---
sections_done = {1: 0, "max": 100}
sections_false = {1: 0}


def make_Chart(xline, yline, ty=1):
    # ---
    Chart = '{| class="floatright sortable"\n|-\n|\n'
    Chart += "{{Graph:Chart"
    # ---
    if ty == 1:
        Chart += "|width=900|height=100|xAxisTitle=property|yAxisTitle=usage|type=rect\n"
    else:
        Chart += "|width=140|height=140|xAxisTitle=value|yAxisTitle=Number|legend=value\n"
        Chart += "|type=pie|showValues1=offset:8,angle:45\n"
    # ---
    Chart += f"|x={xline}\n|y1={yline}"
    # ---
    Chart += "\n}}"
    Chart += "\n|-\n|}"
    # ---
    Chart = Chart.replace("=,", "=")
    # ---
    return Chart


def make_section(P, table, max_n=51):
    """
    Creates a section for a given property in a table.

    Args:
        P (str): The property value.
        table (dict): The table data.

    Returns:
        str: The section text.

    """
    # ---
    # if sections_done[1] >= sections_done['max']:    return ""
    # ---
    Len = table["lenth_of_usage"]
    # ---
    texts = "== {{P|%s}} ==" % P
    # ---
    print(f"make_section for property:{P}")
    texts += f"\n* Total items use these property:{Len:,}"
    if lnnn := table.get("len_prop_claims"):
        texts += f"\n* Total number of claims with these property:{lnnn:,}"
    if len_of_qids := table.get("len_of_qids"):
        texts += f"\n* Number of unique qids:{len_of_qids:,}"
    # ---
    texts += "\n"
    # print(texts)
    # ---
    if not table["qids"]:
        print(f'{P} table["qids"] == empty.')
        return ""
    # ---
    if len(table["qids"]) == 1 and table["qids"].get("others"):
        print(f'{P} table["qids"] == empty.')
        return ""
    # ---
    tables = """{| class="wikitable sortable plainrowheaders"\n|-\n! class="sortable" | #\n! class="sortable" | value\n! class="sortable" | Numbers\n|-\n"""
    # ---
    lists = dict(sorted(table["qids"].items(), key=lambda item: item[1], reverse=True))
    # ---
    num = 0
    other = 0
    # ---
    x_values, y_values = [], []
    # ---
    for x, ye in lists.items():
        # ---
        if x == "others":
            other += ye
            continue
        # ---
        num += 1
        if num < max_n:
            Q = x
            if x.startswith("Q"):
                Q = "{{Q|%s}}" % x
            # ---
            tables += f"\n! {num} \n| {Q} \n| {ye:,} \n|-"
            # ---
            x_values.append(x)
            y_values.append(ye)
            # ---
        else:
            other += ye
    # ---
    num += 1
    # ---
    x_line = ",".join(x_values)
    y_line = ",".join(y_values)
    # ---
    Chart = make_Chart(x_line, y_line, ty=2)
    # ---
    tables += f"\n! {num} \n! others \n! {other:,} \n|-"
    # ---
    tables += "\n|}\n{{clear}}\n"
    # ---
    if "Chart" in sys.argv:
        texts += Chart + "\n\n"
    # ---
    texts += tables
    # ---
    sections_done[1] += 1
    # ---
    return texts


def make_numbers_section(p31list):
    # ---
    rows = []
    # ---
    property_other = 0
    # ---
    nu = 0
    # ---
    x_values, y_values = [], []
    # ---
    for Len, P in p31list:
        nu += 1
        if nu < 27:
            x_values.append(P)
            y_values.append(Len)
        # ---
        if len(rows) < 101:
            Len = f"{Len:,}"
            P = "{{P|%s}}" % P
            lune = f"| {nu} || {P} || {Len} "
            rows.append(lune)
        else:
            property_other += int(Len)
    # ---
    x_line = ",".join(x_values)
    y_line = ",".join(y_values)
    # ---
    Chart2 = make_Chart(x_line, y_line)
    # ---
    rows.append(f"! {nu} \n! others \n! {property_other:,}")
    # ---
    rows = "\n|-\n".join(rows)
    # ---
    table = "\n{| " + f'class="wikitable sortable"\n|-\n! #\n! property\n! usage\n|-\n{rows}\n' + "|}"
    # ---
    texts = "== Numbers ==\n\n"
    # ---
    if "Chart" in sys.argv:
        texts += Chart2 + "\n"
    # ---
    texts += table
    # ---
    return texts


def make_text(tab, ty=""):
    p31list = [[y["lenth_of_usage"], x] for x, y in tab["properties"].items() if y["lenth_of_usage"] != 0]
    p31list.sort(reverse=True)
    # ---
    final = time.time()
    delta = tab.get("delta") or int(final - time_start)
    # ---
    if not tab.get("file_date"):
        tab["file_date"] = "latest"
    # ---
    text = ("<onlyinclude>;dump date {file_date}</onlyinclude>.\n" "* Total items: {All_items:,}\n" "* Items without P31: {items_no_P31:,} \n" "* Items without claims: {items_0_claims:,}\n" "* Items with 1 claim only: {items_1_claims:,}\n" "* Total number of claims: {total_claims:,}\n" "* Number of properties of the report: {len_all_props:,}\n").format_map(tab)
    # ---
    text += f"<!-- bots work done in {delta} secounds --> \n--~~~~~\n"
    chart = make_numbers_section(p31list)
    # ---
    text_p31 = ""
    # ---
    if tab["properties"].get("P31"):
        text_p31 = text + make_section("P31", tab["properties"]["P31"], max_n=501)
        # ---
    # ---
    if "onlyp31" in sys.argv or ty == "onlyp31":
        return text, text_p31
    # ---
    sections = ""
    for _, P in p31list:
        if sections_done[1] >= sections_done["max"]:
            break
        # ---
        sections += make_section(P, tab["properties"][P], max_n=51)
    # ---
    text += f"{chart}\n{sections}"
    # ---
    # text = text.replace("0 (0000)", "0")
    # text = text.replace("0 (0)", "0")
    # ---
    return text, text_p31


if __name__ == "__main__":
    # ---
    with open(items_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # ---
    tab = {
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
    # ---
    for x, g in tab.items():
        if x not in data:
            data[x] = g
    # ---
    if data["len_all_props"] == 0:
        data["len_all_props"] = len(data["properties"])
    # ---
    text, text_p31 = make_text(data, ty="")
    # ---
    with open(claims_new, "w", encoding="utf-8") as outfile:
        outfile.write(text)
    # ---
    print(f"log done to file: {claims_new}")
    # ---
    with open(claims_p31, "w", encoding="utf-8") as outfile:
        outfile.write(text_p31)
    # ---
    print(f"log done to file: {claims_p31}")
