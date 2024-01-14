"""
python3 core8/pwb.py dump/claims/do_text claims_fixed
python3 core8/pwb.py dump/claims/do_text
"""
#
# (C) Ibrahem Qasim, 2023
#
#
import sys
import os
import time
import codecs
import json

# ---
time_start = time.time()
print(f"time_start:{str(time_start)}")
# ---
Dump_Dir = "/data/project/himo/dumps"
# ---
if os.path.exists(r'I:\core\dumps'):
    Dump_Dir = r'I:\core\dumps'
# ---
print(f'Dump_Dir:{Dump_Dir}')
# ---
sections_done = {1: 0, 'max': 100}
sections_false = {1: 0}


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
    Len = table['lenth_of_usage']
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
    print(texts)
    if table["qids"] == {}:
        print(f'{P} table["qids"] == empty.')
        return ""
    # ---
    if len(table["qids"]) == 1 and table["qids"].get("others"):
        print(f'{P} table["qids"] == empty.')
        return ""
    Chart = (
        '{| class="floatright sortable"\n|-\n|\n'
        + "{{Graph:Chart|width=140|height=140|xAxisTitle=value|yAxisTitle=Number\n"
    )
    Chart += "|type=pie|showValues1=offset:8,angle:45\n|x=%s\n|y1=%s\n|legend=value\n}}\n|-\n|}"
    # ---
    tables = """{| class="wikitable sortable plainrowheaders"\n|-\n! class="sortable" | #\n! class="sortable" | value\n! class="sortable" | Numbers\n|-\n"""
    # ---
    lists = dict(
        sorted(table["qids"].items(), key=lambda item: item[1], reverse=True)
    )
    # ---
    xline = ""
    yline = ""
    # ---
    num = 0
    other = 0
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
            xline += f",{x}"
            yline += f",{ye:,}"
        else:
            other += ye
    # ---
    num += 1
    # ---
    Chart %= (xline, yline)
    # ---
    tables += f"\n! {num} \n! others \n! {other:,} \n|-"
    # ---
    tables += "\n|}\n{{clear}}\n"
    # ---
    # texts += Chart.replace("=,", "=") + "\n\n"
    # ---
    texts += tables
    # ---
    sections_done[1] += 1
    # ---
    return texts


def make_numbers_section(p31list):
    xline = ""
    yline = ""
    # ---
    rows = []
    # ---
    property_other = 0
    # ---
    n = 0
    # ---
    for Len, P in p31list:
        n += 1
        if n < 27:
            xline += f",{P}"
            yline += f",{Len}"
        # ---
<<<<<<< HEAD
        if len(rows) < 101:
            Len = f"{Len:,}"
            P = "{{P|%s}}" % P
            lune = f"| {n} || {P} || {Len} "
            rows.append(lune)
        else:
            property_other += int(Len)
    Chart2 = (
        "{| class='floatright sortable' \n|-\n|"
        + "{{Graph:Chart|width=900|height=100|xAxisTitle=property|yAxisTitle=usage|type=rect\n"
    )
    Chart2 += f"|x={xline}\n|y1={yline}"
    Chart2 += "\n}}"
    Chart2 += "\n|-\n|}"
=======
        if x not in priffixes or tab == {}:
            continue
        # ---
        p31list = [[y, xfx] for xfx, y in tab.items()]
        # ---
        try:
            p31list.sort(reverse=True)
        except Exception:
            print('p31list.sort(reverse=True)')
            print(p31list)
        # ---
        rows = []
        c = 1
        li = 100
        # ---
        if x != 'مقالة':
            li = 10
        # ---
        section_others = 0
        # ---
        for xx, yy in p31list:
            if yy != "no":
                if xx > li and len(rows) < 150:
                    yf = "{{Q|%s}}" % yy
                    rows.append(f'| {c} || {yf} || {xx} ')
                    c += 1
                else:
                    section_others += xx
        # ---
        if not rows:
            del p31list
            continue
        tatone = '\n{| class="wikitable sortable"\n! # !! {{P|P31}} !! الاستخدام \n|-\n' + '\n|-\n'.join(rows)
        # ---
        tatone += f'\n|-\n! - !! أخرى !! {section_others}\n|-\n'
        # ---
        tatone += '\n|}\n'
        # ---
        x2 = x.replace(":", "")
        # ---
        del rows, p31list, section_others
        # ---
        textP31 += f"\n=== {x2} ===\n{tatone}"
    # ---
    return textP31


def save_to_wp(text):
    if text == "":
        print('text is empty')
        return
    # ---
    print(text)
    # ---
    if "nosave" in sys.argv or "test" in sys.argv:
        return
    # ---
    title = 'ويكيبيديا:مشروع_ويكي_بيانات/تقرير_P31'
    # ---
    from API import arAPI

    arAPI.page_put(oldtext="", newtext=text, summary='Bot - Updating stats', title=title)
    # ---
    del text
    del arAPI


def read_data():
    filename = '/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2'
    # ---
    if not os.path.isfile(filename):
        print(f'file {filename} <<lightred>> not found')
        return
    # ---
    t1 = time.time()
    # ---
    c = 0
    # ---
    # with bz2.open(filename, "r", encoding="utf-8") as f:
    with bz2.open(filename, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.decode("utf-8").strip("\n").strip(",")
            if line.startswith('{') and line.endswith('}'):
                c += 1
                # ---
                if c > Limit[1]:
                    print('c>Limit[1]')
                    break
                # ---
                if c < Offset[1]:
                    if c % 1000 == 0:
                        dii = time.time() - t1
                        print('Offset c:%d, time:%d' % (c, dii))
                    continue
                # ---
                if (c % 1000 == 0 and c < 100000) or c % 100000 == 0:
                    dii = time.time() - t1
                    print(f'c:{c}, time:{dii}')
                    t1 = time.time()
                    print_memory()
                # ---
                if "printline" in sys.argv and (c % 1000 == 0 or c == 1):
                    print(line)
                # ---
                # جميع عناصر ويكي بيانات المفحوصة
                stats_tab['all_items'] += 1
                # ---
                p31_no_ar_lab = []
                json1 = json.loads(line)
                # ---
                # q = json1['id']
                sitelinks = json1.get('sitelinks', {})
                if not sitelinks or sitelinks == {}:
                    del json1
                    continue
                # ---
                arlink = sitelinks.get('arwiki', {}).get('title', '')
                if not arlink:
                    # عناصر بوصلات لغات بدون وصلة عربية
                    stats_tab['sitelinks_no_ar'] += 1
                    del json1, sitelinks
                    continue
                # ---
                # عناصر ويكي بيانات بها وصلة عربية
                stats_tab['all_ar_sitelinks'] += 1
                arlink_type = "مقالة"
                # ---
                for pri, _ in priffixes.items():
                    if arlink.startswith(pri):
                        priffixes[pri]["count"] += 1
                        arlink_type = pri
                        break
                # ---
                if arlink_type not in stats_tab['p31_main_tab']:
                    stats_tab['p31_main_tab'][arlink_type] = {}
                # ---
                if arlink_type == "مقالة":
                    priffixes["مقالة"]["count"] += 1
                # ---
                p31x = 'no'
                # ---
                claims = json1.get('claims', {})
                # ---
                if claims == {}:
                    # صفحات دون أية خواص
                    stats_tab['no_claims'] += 1
                # ---
                P31 = claims.get('P31', {})
                # ---
                if P31 == {}:
                    # صفحة بدون خاصية P31
                    stats_tab['no_p31'] += 1
                    # ---
                    if len(claims) > 0:
                        # خواص أخرى بدون خاصية P31
                        stats_tab['other_claims_no_p31'] += 1
                # ---
                for x in P31:
                    p31x = x.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
                    if not p31x:
                        continue
                    # ---
                    if p31x not in p31_no_ar_lab:
                        p31_no_ar_lab.append(p31x)
                    # ---
                    if p31x in stats_tab['p31_main_tab'][arlink_type]:
                        stats_tab['p31_main_tab'][arlink_type][p31x] += 1
                    else:
                        stats_tab['p31_main_tab'][arlink_type][p31x] = 1
                # ---
                tat = ['labels', 'descriptions', 'aliases']
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
                    if 'ar' in json1[x]:
                        priffixes[arlink_type][x]["yesar"] += 1
                    else:
                        priffixes[arlink_type][x]["noar"] += 1
                # ---
                ar_desc = json1.get('descriptions', {}).get('ar', False)
                # ---
                if not ar_desc:
                    # استخدام خاصية 31 بدون وصف عربي
                    for x in json1.get('claims', {}).get('P31', []):
                        if p31d := x.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id'):
                            if p31d not in stats_tab['Table_no_ar_lab']:
                                stats_tab['Table_no_ar_lab'][p31d] = 0
                            stats_tab['Table_no_ar_lab'][p31d] += 1


def make_P31_table_no():
    # ---
    Table_no_ar_lab_rows = []
    # ---
    po_list = [[dyy, xxx] for xxx, dyy in stats_tab['Table_no_ar_lab'].items()]
    po_list.sort(reverse=True)
    # ---
    cd = 0
    # ---
    other = 0
    # ---
    for xf, gh in po_list:
        if len(Table_no_ar_lab_rows) < 100:
            cd += 1
            yf = "{{Q|%s}}" % gh
            Table_no_ar_lab_rows.append(f'| {cd} || {yf} || {xf} ')
        else:
            other += 1
    P31_table_no = """\n== استخدام خاصية P31 بدون وصف عربي ==\n""" + """{| class="wikitable sortable"\n! # !! {{P|P31}} !! الاستخدامات\n|-\n"""
    P31_table_no += '\n|-\n'.join(Table_no_ar_lab_rows)
>>>>>>> origin/main
    # ---
    Chart2 = Chart2.replace("=,", "=")
    # ---
    rows.append(f"! {n} \n! others \n! {property_other:,}")
    rows = "\n|-\n".join(rows)
    table = "\n{| " + f'class="wikitable sortable"\n|-\n! #\n! property\n! usage\n|-\n{rows}\n' + "|}"
    return f"== Numbers ==\n\n{Chart2}\n{table}"


def make_text(tab, ty=''):
    p31list = [[y["lenth_of_usage"], x] for x, y in tab["properties"].items() if y["lenth_of_usage"] != 0]
    p31list.sort(reverse=True)
    # ---
    final = time.time()
    delta = tab.get('delta') or int(final - time_start)
    # ---
<<<<<<< HEAD
    if not tab.get('file_date'):
        tab['file_date'] = 'latest'
=======
    stats_tab['delta'] = int(final - start)
    text = "* تقرير تاريخ: latest تاريخ التعديل ~~~~~.\n" + "* جميع عناصر ويكي بيانات المفحوصة: {all_items:,} \n"
    text += "* عناصر ويكي بيانات بها وصلة عربية: {all_ar_sitelinks:,} \n"
    text += "* عناصر بوصلات لغات بدون وصلة عربية: {sitelinks_no_ar:,} \n"
    text += "<!-- bots work done in {delta} secounds --> \n"
    text += "__TOC__\n"
>>>>>>> origin/main
    # ---
    text = ("<onlyinclude>;dump date {file_date}</onlyinclude>.\n" "* Total items: {All_items:,}\n" "* Items without P31: {items_no_P31:,} \n" "* Items without claims: {items_0_claims:,}\n" "* Items with 1 claim only: {items_1_claims:,}\n" "* Total number of claims: {all_claims_2020:,}\n" "* Number of properties of the report: {len_all_props:,}\n").format_map(tab)
    # ---
    text += f"<!-- bots work done in {delta} secounds --> \n--~~~~~\n"
    chart = make_numbers_section(p31list)
    # ---
    text_p31 = ''
    # ---
    if tab["properties"].get('P31'):
        text_p31 = text + make_section('P31', tab["properties"]['P31'], max_n=501)
        # ---
    # ---
    if 'onlyp31' in sys.argv or ty == "onlyp31":
        return text, text_p31
    # ---
    sections = ""
    for _, P in p31list:
        if sections_done[1] >= sections_done['max']:
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
    faf = 'claims'
    # ---
    if 'claims_fixed' in sys.argv:
        if os.path.exists(f"{Dump_Dir}/claims_fixed.json"):
            faf = "claims_fixed"
        else:
            print("claims_fixed.json not found")
    # ---
    filename = f"{Dump_Dir}/{faf}.json"
    # ---
    if 'test' in sys.argv:
        filename = f"{Dump_Dir}/{faf}_test.json"
    # ---
    with open(filename, 'r', encoding='utf-8') as f:
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
        "all_claims_2020": 0,
        "properties": {},
        "langs": {},
    }
    # ---
    for x, g in tab.items():
        if x not in data:
            data[x] = g
    # ---
    text, text_p31 = make_text(data, ty='')
    # ---
    claims_new = f'{Dump_Dir}/texts/claims_new.txt'
    claims_p31 = f'{Dump_Dir}/texts/claims_p31.txt'
    # ---
    if 'test' in sys.argv:
        claims_new = f'{Dump_Dir}/texts/claims_new_test.txt'
        claims_p31 = f'{Dump_Dir}/texts/claims_p31_test.txt'
    # ---
    with codecs.open(claims_new, 'w', encoding='utf-8') as outfile:
        outfile.write(text)
    # ---
    with codecs.open(claims_p31, 'w', encoding='utf-8') as outfile:
        outfile.write(text_p31)
    # ---
    # print(text_p31)
    # ---
    print("log_dump done")
