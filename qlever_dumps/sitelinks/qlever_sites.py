
"""
!
"""
import re
import requests
import urllib.parse

headers = {
    "accept": "application/qlever-results+json",
    "content-type": "application/sparql-query"
}

session = requests.session()
session.headers.update(headers)


def query_qlever(sparql_query, limit=10_000_000):

    url = "https://qlever.cs.uni-freiburg.de/api/wikidata"

    data = {
        "query": sparql_query,
        "send": limit
    }

    response = session.get(url, params=data, timeout=50)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(sparql_query)
        print(response.text)
        return []
    # ---
    res_table = response.json()['res']
    # ---

    def fix_it(z):
        # ---
        z = z.split("^^")[0]
        # ---
        if z.startswith('"') and z.endswith('"'):
            z = z[1:-1]
        # ---
        if z.startswith('<') and z.endswith('>'):
            z = z[1:-1]
        # ---
        if z.count("/entity/") == 1:
            z = z.split("/").pop()
        # ---
        return z
    # ---
    result = [
        [fix_it(z) for z in x]
        for x in res_table
    ]
    # ---
    return result


def get_wiki_lang_usage(x):
    # ---
    wiki = x[0]
    lang = x[1]
    # ---
    usage = int(x[2])
    # ---
    if not lang:
        print(f"no lang: {x=}")
    # ---
    return wiki, lang, usage


def get_sitelinks():
    # ---
    sparql = """
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX schema: <http://schema.org/>
        SELECT ?wiki ?lang (count(*) as ?c)
        WHERE {
            ?item schema:inLanguage ?lang.
            ?item schema:isPartOf ?part.
            ?part wikibase:wikiGroup ?wiki .
        }
        group by ?wiki ?lang
        ORDER BY DESC(?c)
    """

    result = query_qlever(sparql, limit=10_000)

    data = {}

    others = {
        "commons" : 0,
        "species" : 0,
        "mediawiki" : 0,
        "wikidata" : 0,
        "meta" : 0,
        "sources" : 0,
        "wikifunctions" : 0,
        "outreach" : 0,
        "wikimania" : 0,
        "foundation" : 0
    }

    for x in result:
        # ['"120307583"^^<http://www.w3.org/2001/XMLSchema#int>']
        # ---
        wiki, lang, usage = get_wiki_lang_usage(x)
        # ---
        if wiki in others:
            others[wiki] += usage
        else:
            # ---
            data.setdefault(wiki, {})
            data[wiki].setdefault(lang, 0)
            data[wiki][lang] += usage
    # ---
    data["others"] = others
    # ---
    for wiki in data:
        # sort data by usage
        data[wiki] = dict(sorted(data[wiki].items(), key=lambda item: item[1], reverse=True))
    # ---
    return data


def sitelinks_stats():
    sparql = """
        PREFIX wikibase: <http://wikiba.se/ontology#>
        SELECT (COUNT(?item) AS ?all_count)
        WHERE {
            # ?item ^schema:about/wikibase:sitelinks ?sl.
            ?item wikibase:sitelinks ?sl.
        }
        """
    # ---
    all_count = 0
    # ---
    result = query_qlever(sparql)
    # ---
    if result:
        all_count = int(result[0][0])
    # ---
    sparql2 = """
        PREFIX wikibase: <http://wikiba.se/ontology#>
        SELECT (COUNT(?item) AS ?all_count) WHERE {
            # ?item ^schema:about/wikibase:sitelinks ?sl.
            ?item wikibase:sitelinks ?sl .
        FILTER (?sl > 0)
        }
        """
    # ---
    with_sitelinks = 0
    # ---
    result2 = query_qlever(sparql2)
    # ---
    if result2:
        with_sitelinks = int(result2[0][0])
    # ---
    without_sitelinks = all_count - with_sitelinks
    # ---
    print(f"all_count: {all_count:,}, with_sitelinks: {with_sitelinks:,}, without_sitelinks:{without_sitelinks:,}")
    # ---
    return all_count, without_sitelinks


def get_date():

    sparql = """
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX schema: <http://schema.org/>
        SELECT ?dumpdate {
        wikibase:Dump schema:dateModified ?dumpdate
        }
        ORDER BY ASC(?dumpdate)
        LIMIT 1
    """
    result = query_qlever(sparql)
    # ---
    # 2025-09-03T23:04:28Z
    result_date = result[0][0].split("T")[0] if result else ""
    # ---
    print(f"get_date: {result_date}")
    # ---
    return result_date


def get_sitelinks_data():
    # ---
    print("get_sitelinks_data:")
    # ---
    new_data = get_sitelinks()
    # ---
    all_items, items_without_sitelinks = sitelinks_stats()
    # ---
    file_date = get_date()
    # ---
    return {
        "new_data": new_data,
        "all_items": all_items,
        "items_without_sitelinks": items_without_sitelinks,
        "file_date": file_date,
    }
