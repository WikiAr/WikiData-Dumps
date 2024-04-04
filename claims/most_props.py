import re
import json
from pathlib import Path
from newapi.page import MainPage

def get_most_usage(text):
    properties = {}
    for line in text.split('\n'):
        match = re.match(r'\|(\d+)=(\d+)', line)
        if match:
            t1, t2 = match.groups()
            properties[f"P{t1}"] = int(t2)
    sorted_properties = sorted(properties.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_properties[:500])

def log_data(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f)

def main():
    file_path = Path(__file__).parent / "properties.json"
    title = "Template:Number of main statements by property"
    page = MainPage(title, 'www', family='wikidata')
    text = page.get_text()
    data = get_most_usage(text)
    log_data(data, file_path)

if __name__ == "__main__":
    main()
