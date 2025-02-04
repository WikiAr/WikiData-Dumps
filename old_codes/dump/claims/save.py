"""
python3 core8/pwb.py dump/claims/save
"""
#
# (C) Ibrahem Qasim, 2023
#
#
import sys
import os

# ---
from newapi.page import MainPage

# ---
Dump_Dir = "/data/project/himo/bots/dumps"
# ---
if os.path.exists('I:/core/bots/dumps'):
    Dump_Dir = 'I:/core/bots/dumps'
# ---
print(f'Dump_Dir:{Dump_Dir}')
# ---
file_to_title = {
    'claims_new.txt': 'User:Mr. Ibrahem/claims',
    'claims_p31.txt': 'User:Mr. Ibrahem/p31',
}
# ---
if 'test' in sys.argv:
    file_to_title = {
        'claims_new_test.txt': 'User:Mr. Ibrahem/claims/sandbox',
        'claims_p31_test.txt': 'User:Mr. Ibrahem/p31/sandbox',
    }
# ---
for file, title in file_to_title.items():
    if os.path.exists(f"{Dump_Dir}/texts/{file}"):
        # ---
        with open(f"{Dump_Dir}/texts/{file}", "r", encoding="utf-8") as f:
            text = f.read()
        # ---
        if not text.strip():
            print(f'file {file} <<lightred>> empty.')
            continue
        # ---
        if file == 'claims_new.txt' and len(text) < 100000:
            print(f'file {file} <<lightred>> too small.')
            continue
        # ---
        if file == 'claims_p31.txt' and len(text) < 10000:
            print(f'file {file} <<lightred>> too small.')
            continue
        # ---
        page = MainPage(title, "www", family="wikidata")
        textold = page.get_text()
        # ---
        page.save(newtext=text, summary="Bot - Updating stats")
