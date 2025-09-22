
"""
python3 I:/core/bots/wd_dumps/qlever_dumps/props/qlever_bot.py

"""
import re
import requests


headers = {
    "accept": "application/qlever-results+json",
    "content-type": "application/sparql-query"
}

session = requests.session()
session.headers.update(headers)


def print_with_color(text, color):
    color_table = {
        "green": 32,
        "yellow": 33,
        "red": 31
    }
    # ---
    color_m = color_table.get(color, 0)
    # ---
    print(f"\033[{color_m}m{text}\033[0m")


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


def get_all_props():
    sparql = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX wikibase: <http://wikiba.se/ontology#>

        SELECT DISTINCT (concat(strafter(str(?property),"/entity/")) as ?prop) WHERE {
            ?property rdf:type wikibase:Property.
            ?property wikibase:propertyType wikibase:WikibaseItem.
        }
        """

    result = query_qlever(sparql)

    data = []

    for x in result:
        # [['"P9977"']]

        # ?labels ?descriptions ?aliases

        data.append(x[0])
    # ---
    print(f"get_all_props: {len(data):,}")
    # ---
    return data


def one_prop_first_100(prop_main):
    # ---
    sparql = f"""
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wikibase: <http://wikiba.se/ontology#>

        SELECT DISTINCT ?value (COUNT(?value) AS ?count)
        WHERE {{
            VALUES ?prop {{ wdt:{prop_main} }}
            ?item a wikibase:Item .
            ?item ?prop ?value .
        }}
        GROUP BY ?value
        ORDER BY DESC(?count)
    """

    result = query_qlever(sparql, limit=100)

    data = {}
    # ---
    if not result:
        return data
    # ---
    for x in result:
        # ['<http://www.wikidata.org/entity/Q189566>', '"1035"^^<http://www.w3.org/2001/XMLSchema#int>']

        value_match = re.search(r"(Q\d+)", x[0])
        if value_match:
            value = value_match.group(1)
        else:
            continue

        if x[1].isdigit():
            count = int(x[1])
        else:
            count = 0

        data[value] = count
    # ---
    return data


def one_prop_count_all(prop_main):
    # ---
    sparql = f"""
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wikibase: <http://wikiba.se/ontology#>

        SELECT DISTINCT (COUNT(?value) AS ?property_claims_count) (COUNT(DISTINCT ?value) AS ?unique_values) (COUNT(DISTINCT ?item) AS ?items_with_property)
        WHERE {{
            VALUES ?prop {{ wdt:{prop_main} }}
            ?item a wikibase:Item .
            ?item ?prop ?value .
        }}
    """

    result = query_qlever(sparql, limit=10)

    data = {
        "property_claims_count": 0,
        "unique_qids_count": 0,
        "items_with_property": 0
    }
    for x in result:
        # ['"120307583"^^<http://www.w3.org/2001/XMLSchema#int>']

        data['property_claims_count'] = int(x[0])
        # ---
        # unique_values
        data['unique_qids_count'] = int(x[1])
        # ---
        # items_with_property
        data['items_with_property'] = int(x[2])
    # ---
    return data


def one_prop(prop_main, first_100={}):
    # ---
    # print_with_color(f"load one_prop: {prop_main}" + (f", len first_100: {len(first_100)}" if first_100 else ""), "red")
    # ---
    if not first_100:
        first_100 = one_prop_first_100(prop_main) or {}
    # ---
    first_100_sum = sum(first_100.values())
    # ---
    count_all_status = one_prop_count_all(prop_main)
    # ---
    property_claims_count = count_all_status['property_claims_count']
    # ---
    data = {
        # "new" : count_all_status,
        "others": property_claims_count - first_100_sum
    }
    # ---
    data.update(count_all_status)
    # ---
    data["qids"] = first_100
    # ---
    print(f"p \t {prop_main} \t claims: {property_claims_count:,} \t others: {data['others']:,}"
          f"\t unique qids:{data['unique_qids_count']:,} \t items:{data['items_with_property']:,}")
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


def get_props_status():
    print("get_props_status")
    # ---
    all_items = get_all_items()
    # ---
    return {
        "all_items": all_items,
    }


if __name__ == "__main__":
    print(one_prop("P31"))
    print(get_props_status())
