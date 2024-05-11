#!/bin/bash

$HOME/local/bin/python3 core8/pwb.py dump2/most_props

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/read_d.py test test -limit:1000000

# claims

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/claims/do_tab.py test

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/claims/do_text.py test

# labels

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/labels/labels_old_values.py test

$HOME/localx/bin/python3 /data/project/himo/bots/dump_core/dump2/labels/do_tab.py test

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/labels/do_text.py test

# save

$HOME/local/bin/python3 core8/pwb.py dump2/save test
