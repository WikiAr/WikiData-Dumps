#!/bin/bash

$HOME/local/bin/python3 wd_core/dump/labels/labels_old_values.py

$HOME/local/bin/python3 wd_core/dump/labels/read_dump.py

$HOME/local/bin/python3 wd_core/dump/labels/do_text.py

$HOME/local/bin/python3 core8/pwb.py dump/labels/save