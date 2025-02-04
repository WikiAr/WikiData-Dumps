"""

python3 text.py

python3 arw/text.py
python3 dump/arw/text.py

"""
import json
import time
from pathlib import Path

# ---
CHART_TEMPLATE = """
{| class="floatleft sortable" style="text-align:right"
|-
|
{{Graph:Chart|width=170|height=170|xAxisTitle=الشهر|yAxisTitle=عدد المقالات
|type=pie|showValues1=offset:8,angle:45
|x=%s
|y1=%s
|legend=الخاصية
}}
|-
|}"""

TABLE_TEMPLATE = """
{| class="wikitable sortable plainrowheaders"
|-
! class="sortable" rowspan="2" | النطاق
! class="sortable" rowspan="2" | العدد
! class="unsortable" colspan="4" | labels
! class="unsortable" colspan="4" | descriptions
! class="unsortable" colspan="4" | aliases
|-
! نعم !! لا !! عربي !! دون عربي !! نعم !! لا !! عربي !! دون عربي !! نعم !! لا !! عربي !! دون عربي
|-
"""


def generate_table_row(ns, count, nt_labels, nt_descriptions, nt_aliases):
    # ---
    # Remove unnecessary escape characters
    row = f"\n| {ns.replace(':', '')} || {count:,}"

    # Use format_map for better readability and conciseness
    fafa = "\n| {yes:,} || {no:,} || {yesar:,} || {noar:,}"

    # Apply format_map to each category
    row += fafa.format_map(nt_labels)
    row += fafa.format_map(nt_descriptions)
    row += fafa.format_map(nt_aliases)

    # Use the newline character directly for better readability
    return row + "\n|-"


def ns_stats(prefixes):
    texts = """\n== اللغة ==\n"""
    # ---
    tables = TABLE_TEMPLATE
    # ---
    count = prefixes["count"]
    # ---
    table_row = generate_table_row("", count, prefixes["labels"], prefixes["descriptions"], prefixes["aliases"])
    # ---
    tables += table_row
    # ---
    chart = CHART_TEMPLATE % ("'الكل'", count)
    # ---
    texts += chart.replace("=,", "=")
    texts += tables + "\n|}\n"
    # ---
    del tables, chart
    # ---
    return texts


def format_section(section, rows, section_others):
    tr = "\n|-\n"
    section_table = '{| class="wikitable sortable"\n'
    section_table += "! # !! {{P|P31}} !! الاستخدام"
    section_table += tr

    section_table += tr.join(rows)

    section_table += f"{tr}! - !! أخرى !! {section_others}\n"
    section_table += "|}\n"

    return f"=== {section.replace(':', '')} ===\n{section_table}"


def make_text_p31(p31_main_tab):
    formatted_sections = []
    # ---
    for section, tab in p31_main_tab.items():
        if not tab:
            continue

        sorted_items = sorted(tab.items(), key=lambda x: x[1], reverse=True)

        rows = []
        c = 1
        threshold = 100 if section != "مقالة" else 10
        section_others = 0

        for qid, count in sorted_items:
            if qid == "no":
                continue
            if count > threshold and len(rows) < 500:
                yf = "{{Q|%s}}" % qid
                rows.append(f"| {c} || {yf} || {count:,} ")
                c += 1
            else:
                section_others += count

        formatted_section = format_section(section, rows, section_others)
        formatted_sections.append(formatted_section)

        del rows, sorted_items, section_others
    # ---
    return "\n".join(formatted_sections)


def create_p31_table_no(table_no_ar_lab, max_rows=100):
    # ---
    table_no_ar_lab_rows = []
    # ---
    # Sort the items in reverse order based on their values
    sorted_items = sorted(table_no_ar_lab.items(), key=lambda x: x[1], reverse=True)
    # ---
    index = 0
    # ---
    other_count = 0
    # ---
    for qid, count in sorted_items:
        if len(table_no_ar_lab_rows) <= max_rows:
            index += 1
            label_link = "{{Q|%s}}" % qid
            table_no_ar_lab_rows.append(f"| {index} || {label_link} || {count:,} ")
        else:
            other_count += count
    # ---
    # Build the P31 table
    tr = "\n|-\n"
    # ---
    p31_table_no = "\n== استخدام خاصية P31 بدون وصف عربي ==\n"
    # ---
    p31_table_no += '{| class="wikitable sortable"\n! # !! {{P|P31}} !! الاستخدامات'
    # ---
    p31_table_no += tr
    # ---
    p31_table_no += tr.join(table_no_ar_lab_rows)
    # ---
    p31_table_no += f"{tr}! - !! أخرى !! {other_count:,}\n"
    # ---
    p31_table_no += "|}\n"
    # ---
    return p31_table_no


def mainar():
    start = time.time()
    # ---
    items_file = Path(__file__).parent / "arw.json"
    # ---
    with open(items_file, "r", encoding="utf-8") as infile:
        stats_tab = json.load(infile)
    # ---
    final = time.time()
    # ---
    stats_tab["delta"] = int(final - start)
    text = f"* تقرير تاريخ: latest تاريخ التعديل ~~~~~.\n* جميع عناصر ويكي بيانات المفحوصة: {stats_tab['all_items']:,} \n"
    text += "* عناصر ويكي بيانات بها وصلة عربية: {all_ar_sitelinks:,} \n"
    text += "* عناصر بدون وصلات لغات: {no_sitelinks:,} \n"
    text += "* عناصر بوصلات لغات بدون وصلة عربية: {sitelinks_no_ar:,} \n"
    text += "<!-- bots work done in {delta} secounds --> \n"
    text += "__TOC__\n"
    # ---
    text = text.format_map(stats_tab)
    # ---
    priffixes = stats_tab["pages"]
    # ---
    NS_table = ns_stats(priffixes)
    # ---
    P31_secs = f"== استخدام خاصية P31 ==\n* {stats_tab['no_claims']:,} صفحة دون أية خواص.\n"
    P31_secs += "* {no_p31:,} صفحة بدون خاصية P31.\n"
    P31_secs += "* {other_claims_no_p31:,} صفحة بها خواص أخرى دون خاصية P31.\n"
    # ---
    P31_secs = P31_secs.format_map(stats_tab)
    # ---
    textP31 = make_text_p31(stats_tab["p31_main_tab"])
    # ---
    P31_table_no = create_p31_table_no(stats_tab["Table_no_ar_lab"])
    # ---
    text += f"\n{NS_table}"
    text += f"\n{P31_secs}"
    text += f"\n{textP31}"
    text += f"\n{P31_table_no}"
    # ---
    print(text)
    # ---
    if stats_tab["all_items"] == 0:
        print("nothing to update")
        return
    # ---
    with open(Path(__file__).parent / "arw2.txt", "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    mainar()
