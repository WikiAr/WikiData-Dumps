#!/bin/bash

$HOME/localx/bin/python3 /data/project/himo/wd_core/dump/labels/labels_old_values.py

$HOME/localx/bin/python3 /data/project/himo/wd_core/dump/labels/read_dump.py

$HOME/localx/bin/python3 /data/project/himo/wd_core/dump/labels/do_text.py

$HOME/localx/bin/python3 core8/pwb.py dump/labels/save