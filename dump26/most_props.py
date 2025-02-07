"""
from dump.claims.most_props import get_data()
python3 core8/pwb.py dump/claims/most_props
"""
import re
import json
import requests
import sys
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON


def get_query_result(query):
    # TODO: https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/WDQS_graph_split/Rules#Scholarly_Articles

    endpoint_url = "https://query.wikidata.org/sparql"
    # ---
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # ---
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    # ---
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # ---
    data = sparql.query().convert()
    lista = [x for x in data["results"]["bindings"]]
    # ---
    return lista


def get_WikibaseItem_props():
    # ---
    query = """SELECT DISTINCT ?property WHERE {
        ?property rdf:type wikibase:Property.
        ?property wikibase:propertyType wikibase:WikibaseItem.
      }"""

    # ---
    result = get_query_result(query)
    # ---
    lista = []
    # ---
    for x in result:
        prop = x["property"]["value"]
        prop = prop.replace("http://www.wikidata.org/entity/", "")
        lista.append(prop)
    # ---
    print(f"get_WikibaseItem_props: {len(lista)}")
    # ---
    return lista


def get_most_usage(text):
    properties = {}
    for line in text.split("\n"):
        match = re.match(r"\|(\d+)=(\d+)", line)
        if match:
            t1, t2 = match.groups()
            properties[f"P{t1}"] = int(t2)

    itemsprop = get_WikibaseItem_props()

    properties = {x: v for x, v in properties.items() if x in itemsprop}

    sorted_properties = sorted(properties.items(), key=lambda x: x[1], reverse=True)

    return dict(sorted_properties[:101])


def GetPageText_new(title):
    title = title.replace(' ', '_')
    # ---
    url = f'https://wikidata.org/wiki/{title}?action=raw'
    # ---
    print(f"url: {url}")
    # ---
    text = ''
    # ---
    # get url text
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad responses
        text = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page text: {e}")
        return ''
    # ---
    if not text:
        print(f'no text for {title}')
    # ---
    return text


def get_data():
    file_path = Path(__file__).parent / "properties.json"
    # ---
    title = "Template:Number of main statements by property"
    # ---
    text = GetPageText_new(title)
    # ---
    data = get_most_usage(text)
    # ---
    print(f"len of data: {len(data)}")
    # ---
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    # ---
    print(f"saved to {file_path}")
    # ---
    return data


if __name__ == "__main__":
    get_data()
