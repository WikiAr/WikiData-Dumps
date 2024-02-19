#!/bin/bash

$HOME/localx/bin/python3 /data/project/himo/wd_core/dump/claims/read_dump.py

$HOME/localx/bin/python3 /data/project/himo/wd_core/dump/claims/fix_dump.py

$HOME/localx/bin/python3 /data/project/himo/wd_core/dump/claims/do_text.py

#cp dumps/claims.json public_html/claims.json

$HOME/localx/bin/python3 core8/pwb.py dump/claims/save











