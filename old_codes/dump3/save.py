"""

python3 core8/pwb.py dump3/save

"""
import sys
import logging
from pathlib import Path
from newapi.page import MainPage

va_dir = Path(__file__).parent
# ---
texts_dir = va_dir / "texts"
# ---
if "test" in sys.argv:
    texts_dir = va_dir / "texts_test"
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
    file_path = texts_dir / file
    # ---
    if file_path.exists():
        # ---
        text = file_path.read_text(encoding="utf-8")
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
