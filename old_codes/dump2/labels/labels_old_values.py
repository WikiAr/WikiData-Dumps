"""
from dump.labels.labels_old_values import make_old_values# make_old_values()

python3 core8/pwb.py dump2/labels/labels_old_values

"""
from pathlib import Path
import sys
import re
import requests

dir2 = Path(__file__).parent

def GetPageText_new(title):
    title = title.replace(' ', '_')
    # ---
    url = f'https://wikidata.org/wiki/{title}?action=raw'
    # ---
    print(f"url: {url}")
    # ---
    text = ''
    # ---
    session = requests.session()
    session.headers.update({"User-Agent": "Himo bot/1.0 (https://himo.toolforge.org/; tools.himo@toolforge.org)"})
    # ---
    # get url text
    try:
        response = session.get(url, timeout=10)
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

def clean_text(texts):
    # ---
    texts = texts.replace(',', '')
    # ---
    texts = texts.replace('style="background-color:#c79d9d"| ', '')
    texts = texts.replace('style="background-color:#9dc79d"| ', '')
    # ---
    return texts
def from_wiki():
    # ---
    title = 'User:Mr. Ibrahem/Language statistics for items'
    # ---
    if 'test1' in sys.argv:
        title += '/sandbox'
    # ---
    print(f'from_wiki, title: {title}')
    # ---
    texts = GetPageText_new(title)
    # texts = open(f'{dir2}/te.txt', "r", encoding="utf-8").read()
    # ---
    texts = clean_text(texts)
    # ---
    last_total = 0
    if io := re.search(r"\* Total items:(\d+)\.", texts):
        last_total = int(io.group(1))
    Old = {'last_total': last_total}
    # ---
    # ---
    texts = texts.split('|}')[0]
    texts = texts.replace('|}', '')
    for L in texts.split('|-'):
        L = L.strip()
        L = L.replace('\n', '|')
        # ---
        if L.find('{{#language:') != -1:
            L = re.sub(r'\d+\.\d+\%', '', L)
            L = re.sub(r'\|\|\s*\+\d+\s*', '', L)
            L = re.sub(r'\|\|\s*\-\d+\s*', '', L)
            L = re.sub(r'\s*\{\{\#language\:.*?\}\}\s*', '', L)
            L = re.sub(r'\s*\|\|\s*', '||', L)
            L = re.sub(r'\s*\|\s*', '|', L)
            L = L.replace('||||', '||')
            L = L.replace('||||', '||')
            L = L.replace('||||', '||')
            L = L.replace('||||', '||')
            L = L.strip()
            if 'test' in sys.argv:
                print(L)
            if iu := re.search(r"\|(.*?)\|\|(\d*)\|\|(\d*)\|\|(\d*)", L):
                lang = iu.group(1).strip()
                Old[lang] = {'labels': 0, 'descriptions': 0, 'aliases': 0, 'all': 0}

                if iu.group(2):
                    Old[lang]['all'] += int(iu.group(2))
                    Old[lang]['labels'] = int(iu.group(2))

                if iu.group(3):
                    Old[lang]['all'] += int(iu.group(3))
                    Old[lang]['descriptions'] = int(iu.group(3))

                if iu.group(4):
                    Old[lang]['all'] += int(iu.group(4))
                    Old[lang]['aliases'] = int(iu.group(4))

    print(f'get data from page len of old data:{len(Old)}')
    return Old


def make_old_values():
    # ---
    print('get data from page')
    # ---
    Old = from_wiki()
    # ---
    return Old


if __name__ == "__main__":
    make_old_values()
