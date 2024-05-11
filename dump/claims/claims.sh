#!/bin/bash

$HOME/localx/bin/python3 core8/pwb.py dump/most_props

$HOME/localx/bin/python3 /data/project/himo/bots/dump_core/dump/claims/do_tab.py

$HOME/localx/bin/python3 /data/project/himo/bots/dump_core/dump/claims/do_text.py

#cp dumps/claims.json public_html/claims.json

$HOME/localx/bin/python3 core8/pwb.py dump/claims/save











