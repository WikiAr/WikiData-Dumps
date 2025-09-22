#!/usr/bin/env python3
# coding: utf-8
from typing import Dict, Any


class SitelinksReport:

    def __init__(self):
        self.FAMILIES_NAMES: Dict[str, str] = {
            "others": "{{int:wikibase-sitelinks-special}}",
            "wikisource": "{{int:Wikibase-otherprojects-wikisource}}",
            "wikipedia": "{{int:Wikibase-otherprojects-wikipedia}}",
            "wikiquote": "{{int:Wikibase-otherprojects-wikiquote}}",
            "wiktionary": "{{int:Wikibase-otherprojects-wiktionary}}",
            "wikibooks": "{{int:Wikibase-otherprojects-wikibooks}}",
            "wikinews": "{{int:Wikibase-otherprojects-wikinews}}",
            "wikiversity": "{{int:Wikibase-otherprojects-wikiversity}}",
            "wikivoyage": "{{int:Wikibase-otherprojects-wikivoyage}}",
        }
        self.new_data: Dict[str, Any] = {
            "date": "",
            "all_items": 0,
            "items_without_sitelinks": 0,
            "sitelinks": {fam: {} for fam in self.FAMILIES_NAMES},
        }

    @staticmethod
    def make_name(code: str) -> str:
        return f"{{{{int:project-localized-name-{code}}}}}"

    @staticmethod
    def make_link(project_code: str, family: str, code: str) -> str:
        explicit = {
            "wikimaniawiki": "[[:wikimania:|wikimaniawiki]]",
            "metawiki": "[[:m:|metawiki]]",
            "mediawikiwiki": "[[:mw:|mediawikiwiki]]",
            "wikidatawiki": "[[d:|wikidatawiki]]",
            "wikifunctionswiki": "[[:wikifunctions:|wikifunctionswiki]]",
            "specieswiki": "[[:species:|specieswiki]]",
            "outreachwiki": "[[:outreachwiki:|outreachwiki]]",
            "foundationwiki": "[[:foundation:|foundationwiki]]",
            "commonswiki": "[[:c:|commonswiki]]",
        }
        if project_code in explicit:
            return explicit[project_code]

        family_map = {
            "wikisource": "[[:s:{}:|{}]]",
            "wikipedia": "[[:w:{}:|{}]]",
            "wikiquote": "[[:q:{}:|{}]]",
            "wiktionary": "[[:wikt:{}:|{}]]",
            "wikibooks": "[[:b:{}:|{}]]",
            "wikinews": "[[:n:{}:|{}]]",
            "wikiversity": "[[:v:{}:|{}]]",
            "wikivoyage": "[[:voy:{}:|{}]]",
        }
        if family in family_map:
            return family_map[family].format(code, project_code)

        return project_code

    @staticmethod
    def _format_delta(new: int, old: int, add_plus: bool = False) -> str:
        try:
            old_int = int(old)
        except Exception:
            return "0"
        diff = new - old_int
        if add_plus:
            sign = "+" if diff > 0 else ""
            return f"{sign}{diff:,}"
        return f"{diff:,}"

    def make_families_text_u(self, du_tab: Dict[str, Dict[str, Dict[str, int]]]) -> Dict[str, str]:
        result: Dict[str, str] = {}

        for family, sitelinks in du_tab.items():
            rows = []
            new_data_family: Dict[str, int] = {}

            total_links = sum(item.get("new", 0) for item in sitelinks.values())
            family2 = family if family != "others" else "wiki"

            for idx, (code, code_tab) in enumerate(
                sorted(sitelinks.items(), key=lambda x: x[1].get("new", 0), reverse=True),
                start=1,
            ):
                old_count = code_tab.get("old", 0)
                new_count = code_tab.get("new", 0)
                new_data_family[code] = new_count

                delta = new_count - int(old_count) if str(old_count).isdigit() else 0
                plus = "" if delta < 1 else "+"
                color_l = "" if delta == 0 else ("#9dc79d" if delta > 0 else "#c79d9d")
                color_tag = f'style="background-color:{color_l}"|' if color_l else ""

                project_code = f"{code}wiki" if family2 == "wikipedia" else f"{code}{family2}"
                link = self.make_link(project_code, family2, code)
                name_token = self.make_name(project_code)

                row = f"| {idx} || {link} || {name_token} || {new_count:,} || {color_tag} {plus}{delta:,} "
                rows.append(row)

            self.new_data["sitelinks"][family] = dict(
                sorted(new_data_family.items(), key=lambda x: x[1], reverse=True)
            )

            family_name = family
            if self.FAMILIES_NAMES.get(family, family) != family:
                family_name = family + " / " + self.FAMILIES_NAMES.get(family, family)

            section_header = "== " + family_name + " ==\n" if family == "others" else "=== " + family_name + " ===\n"

            section = section_header
            section += f"* Total number of links: {total_links:,}\n"
            section += '{| class="wikitable sortable"\n'
            section += "! # !! Code !! Name !! Number of links !! New \n|-\n"
            section += "\n|-\n".join(rows)
            section += "\n|}\n"

            result[family] = section

        return result

    def make_families_text(self, n_tab: Dict[str, Any]) -> str:
        du_sitelinks = n_tab.get("sitelinks", {})
        families_text = self.make_families_text_u(du_sitelinks)

        sort_list = [
            "others",
            "wikipedia",
            "wiktionary",
            "wikibooks",
            "wikinews",
            "wikiquote",
            "wikisource",
            "wikiversity",
            "wikivoyage",
        ]

        families_text = dict(
            sorted(
                families_text.items(),
                key=lambda kv: sort_list.index(kv[0]) if kv[0] in sort_list else len(sort_list) + 1,
            )
        )

        parts = []
        if "others" in families_text:
            parts.append(families_text.pop("others"))

        parts.append("== sitelinks per family ==\n")

        parts.extend(families_text.values())
        return "\n\n".join(parts)

    def facts(self, n_tab: Dict[str, Any], Old: Dict[str, Any]) -> str:
        total_items_old = int(Old.get("all_items", 0))
        all_items_new = int(n_tab.get("all_items", 0))

        rows = []
        diff = self._format_delta(all_items_new, total_items_old, add_plus=True)

        no_sitelinks = int(n_tab.get("items_without_sitelinks", 0))
        self.new_data["items_without_sitelinks"] = no_sitelinks

        no_sitelinks_diff = self._format_delta(no_sitelinks, Old.get("items_without_sitelinks", 0), add_plus=True)

        rows.append(f"|-\n| Total items last update || {total_items_old:,} || 0 ")
        rows.append(f"|-\n| Total items || {all_items_new:,}  || {diff} ")
        rows.append(f"|-\n| Items without sitelinks || {no_sitelinks:,} || {no_sitelinks_diff} ")

        most = n_tab.get("most", {}).get("sitelinks")
        if most:
            q = most.get("q", "")
            count = most.get("count", 0)
            rows.append("|-\n| Most linked item ([[{}]]) || {:,} || ".format(q, count))

        table = '{| class="wikitable sortable"\n! Title !! Number !! Diff \n'
        table += "\n".join(rows)
        table += "\n|}\n\n"
        return table

    def make_text(self, n_tab: Dict[str, Any]) -> str:
        Old = n_tab.get("old_data", {})
        total_items = n_tab.get("all_items", 0)
        dumpdate = n_tab.get("file_date") or "latest"

        text = f"Update: <onlyinclude>{dumpdate}</onlyinclude>.\n\n"
        text += "--~~~~\n\n"
        text += self.facts(n_tab, Old)
        text += self.make_families_text(n_tab)
        text += "\n[[Category:Wikidata statistics|Sitelinks]]"

        self.new_data["date"] = dumpdate
        self.new_data["all_items"] = total_items

        print(f"make_text composed: total_items={total_items} dumpdate={dumpdate}")
        return text


def make_text(n_tab: Dict[str, Any]) -> str:
    report = SitelinksReport()
    return report.make_text(n_tab)
