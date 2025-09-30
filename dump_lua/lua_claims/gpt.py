#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json


def format_diff(new_val, old_val):
    diff = new_val - old_val
    if diff == 0:
        return "-"
    sign = "+" if diff > 0 else ""
    return f"{sign}{diff}"


def main():
    # Load JSON data
    with open("data/old_data.json", "r", encoding="utf-8") as f:
        old_data = json.load(f)
    with open("data/new_data.json", "r", encoding="utf-8") as f:
        new_data = json.load(f)

    lines = []

    # --- Header table ---
    lines.append('{| class="wikitable sortable"')
    lines.append("! Title !! Number !! Diff")
    lines.append("|-")
    lines.append(f"| Report date || {new_data['date']} || -")
    lines.append("|-")
    lines.append(f"| Total items last update || {old_data['all_items']} || -")
    lines.append("|-")
    lines.append(f"| Total items || {new_data['all_items']} || {format_diff(new_data['all_items'], old_data['all_items'])}")
    lines.append("|-")
    lines.append(f"| Items without P31 || {new_data['items_missing_P31']} || {format_diff(new_data['items_missing_P31'], old_data['items_missing_P31'])}")
    lines.append("|-")
    lines.append(f"| Items without claims || {new_data['items_with_0_claims']} || {format_diff(new_data['items_with_0_claims'], old_data['items_with_0_claims'])}")
    lines.append("|-")
    lines.append(f"| Items with 1 claim only || {new_data['items_with_1_claim']} || {format_diff(new_data['items_with_1_claim'], old_data['items_with_1_claim'])}")
    lines.append("|-")
    lines.append(f"| Total number of claims || {new_data['total_claims_count']} || {format_diff(new_data['total_claims_count'], old_data['total_claims_count'])}")
    lines.append("|-")
    lines.append(f"| Number of properties in the report || {new_data['total_properties_count']} || -")
    lines.append("|}")
    lines.append("\n\n--~~~~\n")

    # --- Numbers section ---
    lines.append("== Numbers ==")
    lines.append('{| class="wikitable sortable"')
    lines.append("|-")
    lines.append("! # !! Property!! Claims !! Diff")

    for idx, pid in enumerate(new_data["properties"].keys(), start=1):
        new_prop = new_data["properties"][pid]
        old_prop = old_data["properties"][pid]
        diff_claims = format_diff(new_prop["property_claims_count"], old_prop["property_claims_count"])
        lines.append("|-")
        lines.append(f"| {idx} || {{{{P|{pid}}}}} || {new_prop['property_claims_count']} || {diff_claims}")

    lines.append("|-")
    lines.append("! 101")
    lines.append("! others || 0 || -")
    lines.append("|}")

    # --- Each property section ---
    for pid, pdata in new_data["properties"].items():
        old_pdata = old_data["properties"][pid]
        lines.append(f"== {{{{P|{pid}}}}} ==")
        lines.append('{| class="wikitable sortable"')
        lines.append("! Title !! Number !! Diff")
        lines.append("|-")
        lines.append(f"| Total items using this property || {pdata['items_with_property']} || {format_diff(pdata['items_with_property'], old_pdata['items_with_property'])}")
        lines.append("|-")
        lines.append(f"| Total number of claims: || {pdata['property_claims_count']} || {format_diff(pdata['property_claims_count'], old_pdata['property_claims_count'])}")
        lines.append("|-")
        lines.append(f"| Number of unique QIDs || {pdata['unique_qids_count']} || {format_diff(pdata['unique_qids_count'], old_pdata['unique_qids_count'])}")
        lines.append("|}")
        lines.append("")
        # qids table
        lines.append('{| class="wikitable sortable plainrowheaders"')
        lines.append("|-")
        lines.append("! class=\"sortable\" | #")
        lines.append("! class=\"sortable\" | value")
        lines.append("! class=\"sortable\" | Numbers")
        lines.append("! class=\"sortable\" | Diff")

        # sort qids by number (desc)
        sorted_qids = sorted(pdata["qids"].items(), key=lambda x: x[1], reverse=True)
        for idx, (qid, num) in enumerate(sorted_qids, start=1):
            old_num = old_pdata["qids"].get(qid, 0)
            lines.append("|-")
            lines.append(f"! {idx}")
            lines.append(f"| {{{{Q|{qid}}}}}")
            lines.append(f"| {num}")
            lines.append(f"| {format_diff(num, old_num)}")

        # others
        lines.append("|-")
        lines.append(f"! {len(sorted_qids)+1}")

        old_others = old_pdata.get("qids_others", 0)
        new_others = pdata.get("qids_others", 0)
        diff = format_diff(new_others, old_others)

        lines.append("! others")
        lines.append(f"! {pdata['qids_others']}")
        lines.append(f"! {diff}")
        lines.append("|}")
        lines.append("{{clear}}")

    # --- Write to file ---
    with open("gpt.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
