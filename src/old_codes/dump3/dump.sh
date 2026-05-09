#!/bin/bash

# tfj run dump3 --mem 2Gi --image python3.9 --command "$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump3/read_json.py"

$HOME/local/bin/python3 core8/pwb.py dump3/most_props

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump3/read_json.py

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump3/claims/do_text.py

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump3/labels/labels_old_values.py

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump3/labels/do_text.py

$HOME/local/bin/python3 core8/pwb.py dump3/save
