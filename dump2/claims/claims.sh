#!/bin/bash

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/read_d.py

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/claims/do_tab.py

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/claims/do_text.py

$HOME/local/bin/python3 core8/pwb.py dump2/claims/save

