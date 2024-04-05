"""
from claims.most_props import get_data()
"""
import re
import json
import sys
from pathlib import Path
from newapi.page import MainPage
from SPARQLWrapper import SPARQLWrapper, JSON



def get_WikibaseItem_props():
    endpoint_url = "https://query.wikidata.org/sparql"
    # ---
    query = """SELECT ?property WHERE {
        ?property rdf:type wikibase:Property.
        ?property wikibase:propertyType wikibase:WikibaseItem.
      }"""

    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # ---
    # TODO adjust user agent; see https://w.wiki/CX6
    # ---
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    # ---
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # ---
    data = sparql.query().convert()
    lista = []
    # ---
    for x in data["results"]["bindings"]:
        prop = x["property"]["value"]
        prop = prop.replace("http://www.wikidata.org/entity/", "")
        lista.append(prop)
    # ---
    return lista

def get_most_usage(text):
    properties = {}
    for line in text.split('\n'):
        match = re.match(r'\|(\d+)=(\d+)', line)
        if match:
            t1, t2 = match.groups()
            properties[f"P{t1}"] = int(t2)

    itemsprop = get_WikibaseItem_props()
    
    properties = {x:v for x,v in properties.items() if x in itemsprop}
    
    sorted_properties = sorted(properties.items(), key=lambda x: x[1], reverse=True)

    return dict(sorted_properties[:500])

def log_data(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f)

def get_data():
    file_path = Path(__file__).parent / "properties.json"
    title = "Template:Number of main statements by property"
    page = MainPage(title, 'www', family='wikidata')
    text = page.get_text()
    data = get_most_usage(text)
    log_data(data, file_path)
    return data

if __name__ == "__main__":
    get_data()
