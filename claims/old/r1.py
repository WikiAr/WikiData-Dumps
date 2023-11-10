import sys
import os
import time
import codecs
import json

time_start = time.time()
print(f"time_start:{str(time_start)}")

Dump_Dir = "/data/project/himo/dumps"

if os.path.exists(r'I:\core\dumps'):
    Dump_Dir = r'I:\core\dumps'

print(f'Dump_Dir:{Dump_Dir}')

sections_done = {
    1: 0,
    'max': 100
}

sections_false = {
    1: 0
}


def make_section(property_value, table_data, max_number=51):
    """
    Creates a section for a given property in a table.

    Args:
        property_value (str): The property value.
        table_data (dict): The table data.

    Returns:
        str: The section text.

    """
    length_of_usage = table_data['lenth_of_usage']

    section_text = "== {{P|%s}} ==" % property_value
    section_text += f"\n* Total items use these property:{length_of_usage:,}"

    length_of_claims = table_data.get("len_prop_claims")
    if length_of_claims:
        section_text += f"\n* Total number of claims with these property:{length_of_claims:,}"

    length_of_qids = table_data.get("len_of_qids")
    if length_of_qids:
        section_text += f"\n* Number of unique qids:{length_of_qids:,}"

    section_text += "\n"

    if table_data["qids"] == {}:
        print(f'{property_value} table_data["qids"] == empty.')
        return ""

    if len(table_data["qids"]) == 1 and table_data["qids"].get("others"):
        print(f'{property_value} table_data["qids"] == empty.')
        return ""

    chart_text = '{| class="floatright sortable"\n|-\n|\n'
    chart_text += "{{Graph:Chart|width=140|height=140|xAxisTitle=value|yAxisTitle=Number\n"
    chart_text += "|type=pie|showValues1=offset:8,angle:45\n|x=%s\n|y1=%s\n|legend=value\n}}\n|-"
    table_text = """{| class="wikitable sortable plainrowheaders"\n|-\n! class="sortable" | #\n! class="sortable" | value\n! class="sortable" | Numbers\n|-\n"""

    sorted_qids = {
        k: v
        for k, v in sorted(table_data["qids"].items(), key=lambda item: item[1], reverse=True)
    }

    x_axis = ""
    y_axis = ""

    count = 0
    other_count = 0

    for qid, qid_count in sorted_qids.items():
        if qid == "others":
            other_count += qid_count
            continue

        count += 1
        if count < max_number:
            Q = qid
            if qid.startswith("Q"):
                Q = "{{Q|%s}}" % qid

            table_text += f"\n! {count} \n| {Q} \n| {qid_count:,} \n|-"

    # Rest of the code...

    return section_text


# Rest of the code...
