# -*- coding: utf-8 -*-
"""

"""

stats_tab = {
    "all_items": 0,
    "all_ar_sitelinks": 0,
    "no_sitelinks": 0,
    "sitelinks_no_ar": 0,
    "no_p31": 0,
    "no_claims": 0,
    "other_claims_no_p31": 0,
    "Table_no_ar_lab": {},
    "p31_main_tab": {"pages": {}},
    "delta": 0,
    "pages": {
        "count": 0,
        "labels": {"yes": 0, "no": 0, "yesar": 0, "noar": 0},
        "descriptions": {"yes": 0, "no": 0, "yesar": 0, "noar": 0},
        "aliases": {"yes": 0, "no": 0, "yesar": 0, "noar": 0},
    },
}


def do_line(json1):
    stats_tab["all_items"] += 1

    sitelinks = json1.get("sitelinks", [])
    if not sitelinks:
        stats_tab["no_sitelinks"] += 1
        del json1
        return

    if "arwiki" not in sitelinks:
        # عناصر بوصلات لغات بدون وصلة عربية
        stats_tab["sitelinks_no_ar"] += 1
        del json1, sitelinks
        return

    # عناصر ويكي بيانات بها وصلة عربية
    stats_tab["all_ar_sitelinks"] += 1
    arlink_type = "pages"
    stats_tab[arlink_type]["count"] += 1

    stats_tab["p31_main_tab"].setdefault(arlink_type, {})

    claims = json1.get("claims", {})

    if not claims:
        # صفحات دون أية خواص
        stats_tab["no_claims"] += 1
    else:
        P31 = claims.get("P31", [])
        if not P31:
            # صفحة بدون خاصية P31
            stats_tab["no_p31"] += 1
            if claims:
                # خواص أخرى بدون خاصية P31
                stats_tab["other_claims_no_p31"] += 1

        ar_desc = "ar" in json1.get("descriptions", [])

        for p31x in P31:
            stats_tab["p31_main_tab"][arlink_type].setdefault(p31x, 0)
            stats_tab["p31_main_tab"][arlink_type][p31x] += 1

            if not ar_desc:
                # استخدام خاصية 31 بدون وصف عربي
                stats_tab["Table_no_ar_lab"].setdefault(p31x, 0)
                stats_tab["Table_no_ar_lab"][p31x] += 1

    for field in ["labels", "descriptions", "aliases"]:
        field_data = json1.get(field, {})
        if not field_data:
            # دون عربي
            stats_tab[arlink_type][field]["no"] += 1
        else:
            stats_tab[arlink_type][field]["yes"] += 1
            # تسمية عربي
            if "ar" in field_data:
                stats_tab[arlink_type][field]["yesar"] += 1
            else:
                stats_tab[arlink_type][field]["noar"] += 1
