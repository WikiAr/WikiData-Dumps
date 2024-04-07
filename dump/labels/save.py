"""
python3 core8/pwb.py dump/labels/save
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
    'labels.txt': 'User:Mr. Ibrahem/Language statistics for items',
    'template.txt': 'Template:Tr langcodes counts',
}
# ---
if 'test' in sys.argv:
    file_to_title = {
        'labels_test.txt': 'User:Mr. Ibrahem/Language statistics for items/sandbox',
        'template_test.txt': 'Template:Tr langcodes counts/sandbox'
    }
# ---
for file, title in file_to_title.items():
    if os.path.exists(f"{Dump_Dir}/texts/{file}"):
        # ---
        with open(f"{Dump_Dir}/texts/{file}", encoding="utf-8") as f:
            text = f.read()
        # ---
        if not text.strip():
            print(f'file {file} <<lightred>> empty.')
            continue
        # ---
        if file == 'labels.txt' and len(text) < 50000:
            print(f'file {file} <<lightred>> too small.')
            continue
        # ---
        if file == 'template.txt' and len(text) < 5000:
            print(f'file {file} <<lightred>> too small.')
            continue
        # ---
        page = MainPage(title, "www", family="wikidata")
        textold = page.get_text()
        # ---
        page.save(newtext=text, summary="Bot - Updating stats")
