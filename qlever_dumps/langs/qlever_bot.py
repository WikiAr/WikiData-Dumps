
"""
!
"""
import requests

headers = {
    "accept": "application/qlever-results+json",
    # "accept-language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    # "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    "content-type": "application/sparql-query"
    # "query-id": "760e8f01-4931-47b7-9ee0-9b566272d6a3",
    # "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    # "sec-ch-ua-mobile": "?0",
    # "sec-ch-ua-platform": '"Windows"',
    # "sec-fetch-dest": "empty",
    # "sec-fetch-mode": "cors",
    # "sec-fetch-site": "same-origin",
    # "referer": "https://qlever.cs.uni-freiburg.de/wikidata/fUx1c1"
}

session = requests.session()
session.headers.update(headers)


def query_qlever(sparql_query, limit=10_000_000):

    # print("--"*20)
    # print(sparql_query)

    # encoded_query = urllib.parse.quote_plus(sparql_query)

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


def one_lang(lang):
    # مثال على استعلام SPARQL
    sparql = f"""
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX schema: <http://schema.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?labels ?descriptions ?aliases WHERE {{
        {{
            SELECT (COUNT(?item) AS ?labels) WHERE {{
	        ?item rdf:type wikibase:Item.
            ?item rdfs:label ?label1 FILTER (LANG(?label1) = "{lang}")
            }}
        }}
        {{
            SELECT (COUNT(?item) AS ?descriptions) WHERE {{
	        ?item rdf:type wikibase:Item.
            ?item schema:description ?desc .
                                    FILTER (LANG(?desc) = "{lang}")
            }}
        }}
        {{
            SELECT (COUNT(DISTINCT ?item) AS ?aliases) WHERE {{
	        ?item rdf:type wikibase:Item.
            ?item skos:altLabel ?alt .
                                FILTER (LANG(?alt) = "{lang}")
            }}
        }}
        }}
    """

    result = query_qlever(sparql, limit=10)

    data = {}

    data = {
        "labels" : 0,
        "descriptions": 0,
        "aliases": 0,
    }
    # ---
    if not result:
        return data
    # ---
    x = result[0]
    # [['"108211994"^^<http://www.w3.org/2001/XMLSchema#int>', '"106527887"^^<http://www.w3.org/2001/XMLSchema#int>', '"14237728"^^<http://www.w3.org/2001/XMLSchema#int>']]

    # ?labels ?descriptions ?aliases

    data['labels'] = int(x[0])
    data['descriptions'] = int(x[1])
    data['aliases'] = int(x[2])

    # ---
    return data


def get_all_items():
    # ---
    sparql = """
        PREFIX wikibase: <http://wikiba.se/ontology#>
        SELECT (COUNT(?item) AS ?all_items)
        WHERE {

        ?item wikibase:sitelinks ?sl.
        }
    """
    # ---
    sparql = """
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT (COUNT(?item) AS ?all_items)
        WHERE {
            ?item rdf:type wikibase:Item.
        }
    """
    # ---
    result = query_qlever(sparql)
    # ---
    all_items = int(result[0][0]) if result else 0
    # ---
    print(f"get_all_items: {all_items}")
    # ---
    return all_items


def get_all_with(ty):
    # ---
    print(f"get_all_with: {ty}:")
    # ---
    tys = {
        "labels": "rdfs:label",
        "descriptions": "schema:description",
        "aliases": "skos:altLabel",
    }
    # ---
    ty = tys.get(ty, "labels")
    # ---
    sparql = f"""
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX schema: <http://schema.org/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT (COUNT(DISTINCT ?item) AS ?c) WHERE {{
            # ?item wikibase:sitelinks ?sl.
            ?item rdf:type wikibase:Item.
            FILTER NOT EXISTS {{
                ?item {ty} ?dd .
            }}
        }}
    """
    # ---
    # print(sparql)
    # ---
    result = query_qlever(sparql)
    # ---
    all_count = int(result[0][0]) if result else 0
    # ---
    print(f" \t {all_count}")
    # ---
    return all_count


def get_most(ty):
    # ---
    print(f"get_most: {ty}:")
    # ---
    tys = {
        "labels": "rdfs:label",
        "descriptions": "schema:description",
        "aliases": "skos:altLabel",
    }
    # ---
    ty = tys.get(ty, "labels")
    # ---
    sparql = f"""
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX schema: <http://schema.org/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?item (COUNT(?label) AS ?lc) WHERE {{
            ?item rdf:type wikibase:Item.
            ?item {ty} ?label .
        }}
        GROUP BY ?item
        ORDER BY DESC(?lc)
        LIMIT 1
    """
    # ---
    # print(sparql)
    # ---
    result = query_qlever(sparql, limit=1)
    # ---
    qid = ""
    count = ""
    # ---
    if result:
        # ---
        qid = result[0][0]
        count = result[0][1]
        # ---
        print(f" \t {qid=}")
        print(f" \t {count=}")
    # ---
    return qid, count


def get_all_withouts(all_items):
    # ---
    items_with_labels = get_all_with("labels")
    items_with_descriptions = get_all_with("descriptions")
    items_with_aliases = get_all_with("aliases")
    # ---
    return {
        "labels": items_with_labels,
        "descriptions": items_with_descriptions,
        "aliases": items_with_aliases
    }


def get_most_status():
    print("get_most_status")
    # ---
    return {
        "labels": get_most("labels"),
        "descriptions": get_most("descriptions"),
        "aliases": get_most("aliases")
    }


def get_langs_status():
    print("get_langs_status")
    # ---
    all_items = get_all_items()
    # ---
    return {
        "all_items": all_items,
        "without": get_all_withouts(all_items)
    }


if __name__ == '__main__':
    # ---
    # print(get_date())
    print(get_most_status())
    # print(one_lang("ar"))
    # ---
