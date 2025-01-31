"""
from dump.labels.labels_old_values import make_old_values# make_old_values()
"""
import os
from pathlib import Path
import json
import sys

import re
import requests

# Compile regex patterns
TOTAL_ITEMS_PATTERN = re.compile(r"\|\s*Total items\s*\|\|\s*\|\|\s*(\d+) \(")
LANGUAGE_STATS_PATTERN = re.compile(r"\|(.*?)\|\|(\d*)\|\|(\d*)\|\|(\d*)")
PERCENTAGE_PATTERN = re.compile(r"\d+\.\d+\%")
DELTA_PATTERN = re.compile(r"\|\|\s*[\+\-]\d+\s*")
LANGUAGE_TEMPLATE_PATTERN = re.compile(r"\s*\{\{\#language\:.*?\}\}\s*")

Session = requests.Session()
dir2 = Path(__file__).parent

file_old_data = f"{dir2}/old_data.json"


def initialize_data_file(file_path):
    """Initialize and load data file with proper error handling."""
    try:
        if not os.path.isfile(file_old_data):
            print(f"create file_old_data:{file_old_data}..")
            with open(file_old_data, "w", encoding="utf-8") as f:
                json.dump({}, f)

        with open(file_old_data, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("langs") or data
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error initializing data file: {e}")
        return {}


_old_data = initialize_data_file(file_old_data)


def GetPageText(title):
    params = {"action": "parse", "prop": "wikitext|sections", "page": title, "format": "json", "utf8": 1}
    # ---
    end_point = "https://www.wikidata.org/w/api.php?"
    # ---
    try:
        response = Session.post(end_point, data=params, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad responses
        json1 = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page text: {e}")
        return ""
    # ---
    if not json1:
        return ""
    # ---
    text = json1.get("parse", {}).get("wikitext", {}).get("*", "")
    # ---
    if not text:
        print(f"no text for {title}")
    # ---
    return text


def from_wiki_new():
    title = "User:Mr. Ibrahem/Language statistics for items"

    if "test1" in sys.argv:
        title += "/sandbox"

    print(f"from_wiki_new, title: {title}")
    texts = GetPageText(title)

    # Apply string replacements
    replacements = {
        ",": "",
        'style="background-color:#c79d9d"| ': "",
        'style="background-color:#9dc79d"| ': "",
    }
    for old, new in replacements.items():
        texts = texts.replace(old, new)

    last_total = 0

    if io := TOTAL_ITEMS_PATTERN.search(texts):
        last_total = int(io.group(1))

    Old = {"last_total": last_total}

    texts = texts.split("== Number of labels, descriptions and aliases for items per language ==")[0]
    texts = texts.replace("|}", "")

    for L in texts.split("|-"):
        L = L.strip()
        L = L.replace("\n", "|")

        if L.find("{{#language:") != -1:
            L = PERCENTAGE_PATTERN.sub("", L)
            L = DELTA_PATTERN.sub("", L)
            L = LANGUAGE_TEMPLATE_PATTERN.sub("", L)
            L = re.sub(r"\s*\|\|\s*", "||", L)
            L = re.sub(r"\s*\|\s*", "|", L)

            while "||||" in L:
                L = L.replace("||||", "||")

            L = L.strip()
            if "test" in sys.argv:
                print(L)

            if iu := LANGUAGE_STATS_PATTERN.search(L):
                lang = iu.group(1).strip()
                Old[lang] = {"labels": 0, "descriptions": 0, "aliases": 0, "all": 0}


def from_wiki():
    # ---
    title = "User:Mr. Ibrahem/Language statistics for items"
    # ---
    if "test1" in sys.argv:
        title += "/sandbox"
    # ---
    print(f"from_wiki, title: {title}")
    # ---
    texts = GetPageText(title)
    # texts = open(f'{dir2}/te.txt', "r", encoding="utf-8").read()
    # ---
    texts = texts.replace(",", "")
    # ---
    texts = texts.replace('style="background-color:#c79d9d"| ', "")
    texts = texts.replace('style="background-color:#9dc79d"| ', "")
    # ---
    last_total = 0
    # | Total items ||  || 113,566,334 (+5,771,637)
    if io := re.search(r"\|\s*Total items\s*\|\|\s*\|\|\s*(\d+) \(", texts):
        last_total = int(io.group(1))
    # ---
    Old = {"last_total": last_total}
    # ---
    texts = texts.split("== Number of labels, descriptions and aliases for items per language ==")[0]
    texts = texts.replace("|}", "")
    # ---
    for L in texts.split("|-"):
        L = L.strip()
        L = L.replace("\n", "|")
        # ---
        if L.find("{{#language:") != -1:
            L = re.sub(r"\d+\.\d+\%", "", L)
            L = re.sub(r"\|\|\s*\+\d+\s*", "", L)
            L = re.sub(r"\|\|\s*\-\d+\s*", "", L)
            L = re.sub(r"\s*\{\{\#language\:.*?\}\}\s*", "", L)
            L = re.sub(r"\s*\|\|\s*", "||", L)
            L = re.sub(r"\s*\|\s*", "|", L)
            L = L.replace("||||", "||")
            L = L.replace("||||", "||")
            L = L.replace("||||", "||")
            L = L.replace("||||", "||")
            L = L.strip()
            if "test" in sys.argv:
                print(L)
            if iu := re.search(r"\|(.*?)\|\|(\d*)\|\|(\d*)\|\|(\d*)", L):
                lang = iu.group(1).strip()
                Old[lang] = {"labels": 0, "descriptions": 0, "aliases": 0, "all": 0}

                if iu.group(2):
                    Old[lang]["all"] += int(iu.group(2))
                    Old[lang]["labels"] = int(iu.group(2))

                if iu.group(3):
                    Old[lang]["all"] += int(iu.group(3))
                    Old[lang]["descriptions"] = int(iu.group(3))

                if iu.group(4):
                    Old[lang]["all"] += int(iu.group(4))
                    Old[lang]["aliases"] = int(iu.group(4))

    print(f"get data from page len of old data:{len(Old)}")
    return Old


def make_old_values():
    # ---
    if len(_old_data) > 5 and "old" in sys.argv:
        print("data in the file..")
        json.dump(_old_data, open(file_old_data, "w", encoding="utf-8"), indent=2)
        return _old_data
    # ---
    print("get data from page")
    # ---
    Old = from_wiki()
    # ---
    try:
        with open(file_old_data, "w", encoding="utf-8") as f:
            json.dump(Old, f, indent=2)
    except IOError as e:
        print(f"Error writing to {file_old_data}: {e}")
    # ---
    return Old


if __name__ == "__main__":
    make_old_values()
