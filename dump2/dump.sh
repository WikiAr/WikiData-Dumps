#!/bin/bash

$HOME/local/bin/python3 core8/pwb.py dump/most_props

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/read_d.py

# claims

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/claims/do_tab.py

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/claims/do_text.py

# labels

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/labels/labels_old_values.py

$HOME/localx/bin/python3 /data/project/himo/bots/dump_core/dump2/labels/do_tab.py

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/labels/do_text.py

# save

$HOME/local/bin/python3 core8/pwb.py dump2/save
