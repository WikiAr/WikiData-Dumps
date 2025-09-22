"""
!
"""
import tqdm

texts_tab = {}

sections_done = {"current": 0, "max": 100}


def min_it(new, old, add_plus=False):
    old = str(old)
    # ---
    if old.isdigit():
        old = int(old)
    else:
        return 0
    # ---
    if old == 0 or new == 0 or new == old:
        return ""
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
    last_total = Old.get("all_items", 0)
    # ---
    text = '{| class="wikitable sortable"\n'
    text += "! Title !! Number !! Diff \n"
    # ---
    texts = {
        "all_items": "Total items",
        "items_missing_P31": "Items without P31",
        "items_with_0_claims": "Items without claims",
        "items_with_1_claim": "Items with 1 claim only",
        "total_claims_count": "Total number of claims",
        "total_properties_count": "Number of properties in the report",
    }
    # ---
    report_date = n_tab.get('file_date') or n_tab.get('date') or "latest"
    # ---
    text += f"|-\n| Report date || {report_date} ||  \n"
    text += f"|-\n| Total items last update || {last_total:,} ||  \n"
    # ---
    for key, title in texts.items():
        # ---
        value = n_tab.get(key, 0)
        # ---
        diff = min_it_tab(n_tab, Old, key, add_plus=True)
        # ---
        text += f"|-\n| {title} || {value:,} || {diff} \n"
    # ---
    text += "|}\n\n"
    # ---
    return text


def pid_section_facts(table, old_data):
    # ---
    table["items_with_property"] = table.get("items_with_property") or table.get("len_of_usage", 0)
    old_data["items_with_property"] = old_data.get("items_with_property") or old_data.get("len_of_usage", 0)
    # ---
    text = '{| class="wikitable sortable"\n'
    text += "! Title !! Number !! Diff \n"
    # ---
    texts_tab_x = {
        "items_with_property": "Total items using this property",
        "property_claims_count": "Total number of claims:",
        "unique_qids_count": "Number of unique QIDs",
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


def make_section(pid, table):
    # ---
    if sections_done["current"] >= sections_done["max"]:
        texts_tab[pid] = ""
        return ""
    # ---
    old_data = table.get("old", {})
    # ---
    old_data_qids = old_data.get("qids") or {}
    # ---
    new_data_qids = table.get("qids") or {"others": 0}
    # ---
    table_rows = []
    # ---
    sorted_qids = dict(sorted(new_data_qids.items(), key=lambda item: item[1], reverse=True))
    # ---
    other_count = table["qids"].get("others", 0) or table.get("qids_others", 0)
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
    _diff_others = min_it(other_count, old_others, add_plus=True)
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
    other_count = 0
    # ---
    max_v = 500
    idx = 0
    # ---
    for idx, (prop, prop_tab) in enumerate(properties_infos.items(), start=1):
        # ---
        if len(rows) < max_v:
            # ---
            # usage = prop_tab.get("items_with_property", 0)
            usage = prop_tab.get("property_claims_count", 0)
            # ---
            old_prop = prop_tab.get("old", {})
            # ---
            old_usage = old_prop.get("property_claims_count")
            diff = min_it(usage, old_usage, add_plus=True)
            # ---
            # value_in_most_props = most_props.get(prop, 0)
            # line = f"| {idx} || {{{{P|{prop}}}}} || {usage:,} <!-- {value_in_most_props:,} -->|| {diff}"
            # ---
            line = f"| {idx} || {{{{P|{prop}}}}} || {usage:,} || {diff}"
            # ---
            # property_claims_count = prop_tab.get("property_claims_count", 0)
            # diff2 = min_it_tab(prop_tab, old_prop, "property_claims_count", add_plus=True)
            # # ---
            # line += f" || {property_claims_count:,}  || {diff2}"
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
    properties_infos = dict(sorted(data["properties"].items(), key=lambda x: x[1].get("property_claims_count", 0), reverse=True))
    # ---
    print(f"{len(properties_infos)=}")
    # ---
    metadata = facts(data, Old)
    # ---
    metadata += "\n--~~~~\n\n"
    # ---
    numbers_section = make_numbers_section(properties_infos, Old)
    # ---
    sections = ""
    # ---
    section_done = 0
    # ---
    for prop, prop_tab in tqdm.tqdm(properties_infos.items(), desc="def make_section(): "):
        # ---
        if section_done < 11:
            sections += make_section(prop, prop_tab)
            # ---
            section_done += 1
    # ---
    return metadata + numbers_section + sections
