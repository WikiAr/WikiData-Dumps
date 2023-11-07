#!/bin/bash

$HOME/local/bin/python3 wd_core/dump/claims/read_dump.py

$HOME/local/bin/python3 wd_core/dump/claims/fix_dump.py

$HOME/local/bin/python3 wd_core/dump/claims/do_text.py

#cp dumps/claims.json public_html/claims.json

$HOME/local/bin/python3 core8/pwb.py dump/claims/save











