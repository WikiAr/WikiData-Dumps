"""
from dump.claims.most_props import get_data()
python3 core8/pwb.py dump26/most_props2
"""
import sys
import re
import json
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON
import requests

sys.path.append(str(Path(__file__).parent.parent))

from dir_handler import most_props_path


class WikidataPropertyAnalyzer:
    def __init__(self):
        self.endpoint_url = "https://query.wikidata.org/sparql"
        self.user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
        self.file_path = most_props_path

    def get_query_result(self, query):
        """
        Executes a SPARQL query and returns the results as a list.
        """
        sparql = SPARQLWrapper(self.endpoint_url, agent=self.user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)

        data = sparql.query().convert()
        return [x for x in data["results"]["bindings"]]

    def get_WikibaseItem_props(self):
        """
        Retrieves all WikibaseItem properties from Wikidata.
        """
        query = """SELECT DISTINCT ?property WHERE {
            ?property rdf:type wikibase:Property.
            ?property wikibase:propertyType wikibase:WikibaseItem.
        }"""

        result = self.get_query_result(query)
        lista = []

        for x in result:
            prop = x["property"]["value"]
            prop = prop.replace("http://www.wikidata.org/entity/", "")
            lista.append(prop)

        print(f"get_WikibaseItem_props: {len(lista)}")
        return lista

    def get_most_usage(self, text):
        """
        Analyzes the usage of properties and returns the top 101 most used ones.
        """
        properties = {}
        for line in text.split("\n"):
            match = re.match(r"\|(\d+)=(\d+)", line)
            if match:
                t1, t2 = match.groups()
                properties[f"P{t1}"] = int(t2)

        itemsprop = self.get_WikibaseItem_props()

        # Filter properties to include only those that are WikibaseItem types
        properties = {x: v for x, v in properties.items() if x in itemsprop}

        # Sort properties by usage count in descending order
        sorted_properties = sorted(properties.items(), key=lambda x: x[1], reverse=True)

        return dict(sorted_properties[:101])

    def get_page_text(self, title):
        """
        Fetches the raw text of a Wikidata page.
        """
        title = title.replace(' ', '_')
        url = f'https://wikidata.org/wiki/{title}?action=raw'

        print(f"url: {url}")
        text = ''
        # ---
        session = requests.session()
        session.headers.update({"User-Agent": "Himo bot/1.0 (https://himo.toolforge.org/; tools.himo@toolforge.org)"})
        # ---
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses
            text = response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page text: {e}")

        if not text:
            print(f'no text for {title}')

        return text

    def save_data(self, data):
        """
        Saves the data to a JSON file.
        """
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        print(f"saved to {self.file_path}")

    def get_data(self):
        """
        Main method to fetch and process data.
        """
        title = "Template:Number of main statements by property"
        text = self.get_page_text(title)

        data = self.get_most_usage(text)

        print(f"len of data: {len(data)}")
        self.save_data(data)

        return data


def get_data():
    analyzer = WikidataPropertyAnalyzer()
    data = analyzer.get_data()
    return data


if __name__ == "__main__":
    get_data()
