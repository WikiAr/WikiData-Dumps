"""
python3 core8/pwb.py dump2/save
"""
import sys
import os
import logging
from newapi.page import MainPage

# ---
texts_dir = "/data/project/himo/bots/dump_core/dump2/texts/"
# ---
if "test" in sys.argv:
    texts_dir = "/data/project/himo/bots/dump_core/dump2/texts_test/"
# ---
logging.info(f"texts_dir:{texts_dir}")
# ---
file_to_title = {
    "claims_new.txt": "User:Mr. Ibrahem/claims",
    "claims_p31.txt": "User:Mr. Ibrahem/p31",
    "labels.txt": "User:Mr. Ibrahem/Language statistics for items",
    "template.txt": "Template:Tr langcodes counts",
}
# ---
file_lengths = {
    "claims_new.txt": 100000,
    "claims_p31.txt": 10000,
    "labels.txt": 50000,
    "template.txt": 5000
}
# ---
for file, title in file_to_title.items():
    # ---
    if "test" in sys.argv:
        title += "/sandbox"
    # ---
    file_path = f"{texts_dir}/{file}"
    # ---
    if os.path.exists(file_path):
        # ---
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        # ---
        if not text.strip():
            logging.info(f"file {file} <<lightred>> empty.")
            continue
        # ---
        for file, min_length in file_lengths.items():
            if len(text) < min_length:
                logging.info(f"file {file} <<lightred>> too small.")
                continue
        # ---
        page = MainPage(title, "www", family="wikidata")
        # ---
        textold = page.get_text()
        # ---
        page.save(newtext=text, summary="Bot - Updating stats", nocreate=0)
