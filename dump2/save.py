"""
python3 core8/pwb.py dump2/save
"""
import sys
import os
from newapi.page import MainPage

# ---
texts_dir = "/data/project/himo/bots/dump_core/dump2/texts/"
# ---
if "test" in sys.argv:
    texts_dir = "/data/project/himo/bots/dump_core/dump2/texts_test/"
# ---
print(f"texts_dir:{texts_dir}")
# ---
file_to_title = {
    "claims_new.txt": "User:Mr. Ibrahem/claims",
    "claims_p31.txt": "User:Mr. Ibrahem/p31",
    "labels.txt": "User:Mr. Ibrahem/Language statistics for items",
    "template.txt": "Template:Tr langcodes counts",
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
        with open(file_path, encoding="utf-8") as f:
            text = f.read()
        # ---
        if not text.strip():
            print(f"file {file} <<lightred>> empty.")
            continue
        # ---
        if file == "claims_new.txt" and len(text) < 100000:
            print(f"file {file} <<lightred>> too small.")
            continue
        # ---
        if file == "claims_p31.txt" and len(text) < 10000:
            print(f"file {file} <<lightred>> too small.")
            continue
        # ---
        if file == "labels.txt" and len(text) < 50000:
            print(f"file {file} <<lightred>> too small.")
            continue
        # ---
        if file == "template.txt" and len(text) < 5000:
            print(f"file {file} <<lightred>> too small.")
            continue
        # ---
        page = MainPage(title, "www", family="wikidata")
        textold = page.get_text()
        # ---
        page.save(newtext=text, summary="Bot - Updating stats")
