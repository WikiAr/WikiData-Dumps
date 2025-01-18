"""

python3 core8/pwb.py dump25/arw/save

"""
import sys
from pathlib import Path
from API import arAPI

title = "ويكيبيديا:مشروع_ويكي_بيانات/تقرير_P31"
# ---
if "test" in sys.argv:
    title += "/ملعب"
# ---
print(f"title:{title}")
# ---
file = Path(__file__).parent / "arw2.txt"
# ---
with open(file, "r", encoding="utf-8") as f:
    text = f.read()
# ---
print(f"len of text: {len(text)}")
# ---
arAPI.page_put(oldtext="", newtext=text, summary="Bot - Updating stats", title=title)
