"""

python3 core8/pwb.py dump3/arw/do_text

"""
import sys
import json
import time
from pathlib import Path

from dump3.arw.p31_table import make_text_p31, create_p31_table_no, ns_stats
from API import arAPI

va_dir = Path(__file__).parent
# ---
do_test = "test" in sys.argv
# ---
items_file = va_dir / "jsons/items.json"
priffix_file = va_dir / "jsons/priffix.json"
# ---
if do_test:
    items_file = va_dir / "jsons/items_test.json"
    priffix_file = va_dir / "jsons/priffix_test.json"


def save_to_wp(text):
    if not text:
        print("text is empty")
        return
    # ---
    print(text)
    # ---
    if "nosave" in sys.argv:
        print("nosave")
        return
    # ---
    title = "ويكيبيديا:مشروع_ويكي_بيانات/تقرير_P31"
    # ---
    if "test" in sys.argv:
        title += "/ملعب"
    # ---
    print(f"title:{title}")
    # ---
    arAPI.page_put(oldtext="", newtext=text, summary="Bot - Updating stats", title=title)


def mainar():
    start = time.time()
    # ---
    with open(items_file, "r", encoding="utf-8") as infile:
        stats_tab = json.load(infile)
    # ---
    with open(priffix_file, "r", encoding="utf-8") as infile:
        priffixes = json.load(infile)
    # ---
    final = time.time()
    # ---
    stats_tab["delta"] = int(final - start)
    text = f"* تقرير تاريخ: latest تاريخ التعديل ~~~~~.\n* جميع عناصر ويكي بيانات المفحوصة: {stats_tab['all_items']:,} \n"
    text += "* عناصر ويكي بيانات بها وصلة عربية: {all_ar_sitelinks:,} \n"
    text += "* عناصر بوصلات لغات بدون وصلة عربية: {sitelinks_no_ar:,} \n"
    text += "<!-- bots work done in {delta} secounds --> \n"
    text += "__TOC__\n"
    # ---
    text = text.format_map(stats_tab)
    # ---
    NS_table = ns_stats(priffixes)
    # ---
    P31_secs = f"== استخدام خاصية P31 ==\n* {stats_tab['no_claims']:,} صفحة دون أية خواص.\n"
    P31_secs += "* {no_p31:,} صفحة بدون خاصية P31.\n"
    P31_secs += "* {other_claims_no_p31:,} صفحة بها خواص أخرى دون خاصية P31.\n"
    # ---
    P31_secs = P31_secs.format_map(stats_tab)
    # ---
    textP31 = make_text_p31(stats_tab["p31_main_tab"], priffixes)
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
    save_to_wp(text)
    # ---
    if "test" not in sys.argv and "nodump" not in sys.argv:
        with open(va_dir / "texts/arw2.txt", "w", encoding="utf-8") as f:
            f.write(text)


if __name__ == "__main__":
    mainar()
