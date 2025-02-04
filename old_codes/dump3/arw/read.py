#!/usr/bin/env python3
"""
toolforge jobs run arw2 --mem 1Gi --image python3.9 --command "$HOME/local/bin/python3 $HOME/core8/pwb.py dump3/arw/arw2"

python3 core8/pwb.py dump3/arw/read
python3 core8/pwb.py dump3/arw/arw2 test ask
python3 core8/pwb.py dump3/arw/arw2 test ask p31
python3 core8/pwb.py dump3/arw/arw2 test ask printline
python3 core8/pwb.py dump3/arw/arw2 test ask limit:5000
"""
import sys
import os
import bz2
import psutil
import json
import time
from pathlib import Path

# ---
bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
# ---
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
# ---
Offset = {1: 0}
# ---
Limit = {1: 9000000000} if "test" not in sys.argv else {1: 15000}
# ---
for arg in sys.argv:
    arg, _, value = arg.partition(":")
    if arg.startswith("-"):
        arg = arg[1:]
    if arg in ["offset", "off"]:
        Offset[1] = int(value)
    if arg == "limit":
        Limit[1] = int(value)

priffixeso = [
    "مقالة",
    "نقاش:",
    "مستخدم:",
    "نقاش المستخدم:",
    "ويكيبيديا:",
    "نقاش ويكيبيديا:",
    "ملف:",
    "نقاش الملف:",
    "ميدياويكي:",
    "نقاش ميدياويكي:",
    "قالب:",
    "نقاش القالب:",
    "مساعدة:",
    "نقاش المساعدة:",
    "تصنيف:",
    "نقاش التصنيف:",
    "بوابة:",
    "نقاش البوابة:",
    "وحدة:",
    "نقاش الوحدة:",
    "إضافة:",
    "نقاش الإضافة:",
    "تعريف الإضافة:",
    "نقاش تعريف الإضافة:",
    "موضوع:",
]
# ---
priffixes = {
    x: {
        "count": 0,
        "labels": {"yes": 0, "no": 0, "yesar": 0, "noar": 0},
        "descriptions": {"yes": 0, "no": 0, "yesar": 0, "noar": 0},
        "aliases": {"yes": 0, "no": 0, "yesar": 0, "noar": 0},
    }
    for x in priffixeso
}
# ---
stats_tab = {
    "all_items": 0,
    "all_ar_sitelinks": 0,
    "sitelinks_no_ar": 0,
    "no_p31": 0,
    "no_claims": 0,
    "other_claims_no_p31": 0,
    "Table_no_ar_lab": {},
    "p31_main_tab": {},
    "delta": 0,
}


def print_memory():
    yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    print(yellow % "Memory usage:", purple % f"{usage} MB")


def read_data():
    filename = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
    # ---
    if not os.path.isfile(filename):
        print(f"file {filename} <<lightred>> not found")
        return
    # ---
    t1 = time.time()
    # ---
    c = 0
    # ---
    with bz2.open(filename, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip("\n").strip(",")
            if line.startswith("{") and line.endswith("}"):
                c += 1
                # ---
                if c > Limit[1]:
                    print(f"c:{c}>Limit[1]:{Limit[1]}")
                    break
                # ---
                if c < Offset[1]:
                    if c % 1000 == 0:
                        dii = time.time() - t1
                        print(f"Offset c:{c}, time:{dii}")
                    continue
                # ---
                if (c % 1000 == 0 and c < 100000) or c % 100000 == 0:
                    dii = time.time() - t1
                    print(f"c:{c}, time:{dii}")
                    t1 = time.time()
                    print_memory()
                # ---
                if "printline" in sys.argv and (c % 1000 == 0 or c == 1):
                    print(line)
                # ---
                # جميع عناصر ويكي بيانات المفحوصة
                stats_tab["all_items"] += 1
                # ---
                # p31_no_ar_lab = []
                # json1 = json.loads(line)
                try:
                    json1 = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    continue
                # ---
                # q = json1['id']
                sitelinks = json1.get("sitelinks", {})
                if not sitelinks:
                    del json1
                    continue
                # ---
                arlink = sitelinks.get("arwiki", {}).get("title", "")
                if not arlink:
                    # عناصر بوصلات لغات بدون وصلة عربية
                    stats_tab["sitelinks_no_ar"] += 1
                    del json1, sitelinks
                    continue
                # ---
                # عناصر ويكي بيانات بها وصلة عربية
                stats_tab["all_ar_sitelinks"] += 1
                arlink_type = "مقالة"
                # ---
                for pri, _ in priffixes.items():
                    if arlink.startswith(pri):
                        priffixes[pri]["count"] += 1
                        arlink_type = pri
                        break
                # ---
                if arlink_type not in stats_tab["p31_main_tab"]:
                    stats_tab["p31_main_tab"][arlink_type] = {}
                # ---
                if arlink_type == "مقالة":
                    priffixes["مقالة"]["count"] += 1
                # ---
                p31x = "no"
                # ---
                claims = json1.get("claims", {})
                # ---
                if not claims:
                    # صفحات دون أية خواص
                    stats_tab["no_claims"] += 1
                # ---
                P31 = claims.get("P31", {})
                # ---
                if not P31:
                    # صفحة بدون خاصية P31
                    stats_tab["no_p31"] += 1
                    # ---
                    if len(claims) > 0:
                        # خواص أخرى بدون خاصية P31
                        stats_tab["other_claims_no_p31"] += 1
                # ---
                for x in P31:
                    p31x = x.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
                    if not p31x:
                        continue
                    # ---
                    # if p31x not in p31_no_ar_lab:
                    #     p31_no_ar_lab.append(p31x)
                    # ---
                    if p31x in stats_tab["p31_main_tab"][arlink_type]:
                        stats_tab["p31_main_tab"][arlink_type][p31x] += 1
                    else:
                        stats_tab["p31_main_tab"][arlink_type][p31x] = 1
                # ---
                tat = ["labels", "descriptions", "aliases"]
                # ---
                for x in tat:
                    if x not in json1:
                        # دون عربي
                        priffixes[arlink_type][x]["no"] += 1
                        continue
                    # ---
                    priffixes[arlink_type][x]["yes"] += 1
                    # ---
                    # تسمية عربي
                    if "ar" in json1[x]:
                        priffixes[arlink_type][x]["yesar"] += 1
                    else:
                        priffixes[arlink_type][x]["noar"] += 1
                # ---
                ar_desc = json1.get("descriptions", {}).get("ar", False)
                # ---
                if not ar_desc:
                    # استخدام خاصية 31 بدون وصف عربي
                    for x in json1.get("claims", {}).get("P31", []):
                        if p31d := x.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id"):
                            if p31d not in stats_tab["Table_no_ar_lab"]:
                                stats_tab["Table_no_ar_lab"][p31d] = 0
                            stats_tab["Table_no_ar_lab"][p31d] += 1


def start():
    start = time.time()
    # ---
    read_data()
    # ---
    with open(items_file, "w", encoding="utf-8") as outfile:
        json.dump(stats_tab, outfile)
    # ---
    with open(priffix_file, "w", encoding="utf-8") as outfile:
        json.dump(priffixes, outfile)
    # ---
    print(f"Total time: {time.time() - start}")


if __name__ == "__main__":
    start()
