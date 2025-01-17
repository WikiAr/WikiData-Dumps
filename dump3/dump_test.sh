#!/bin/bash
$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump3/most_props.py

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump3/read_json.py test -limit:100000

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump3/claims/do_text.py test

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump3/labels/labels_old_values.py test

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump3/labels/do_text.py test

$HOME/local/bin/python3 core8/pwb.py dump3/save test ask diff
