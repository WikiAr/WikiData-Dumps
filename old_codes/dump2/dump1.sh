
#!/bin/bash
cd $HOME

# tfj run dumps --mem 2Gi --image tf-python39 --command "/data/project/himo/bots/dump_core/dump2/dump.sh"

$HOME/local/bin/python3 core8/pwb.py dump2/most_props

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/read_d.py test -limit:5000000

# claims

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/claims/do_tab.py

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/claims/do_text.py

# labels

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/labels/labels_old_values.py

$HOME/localx/bin/python3 /data/project/himo/bots/dump_core/dump2/labels/do_tab.py

$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump2/labels/do_text.py

# save

$HOME/local/bin/python3 core8/pwb.py dump2/save
