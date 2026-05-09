import bz2
import os
from datetime import datetime

import tqdm
from humanize import naturalsize

bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"

file_size = os.path.getsize(bz2_file)

print(naturalsize(file_size, binary=True))

# Get the time of last modification
last_modified_time = os.path.getmtime(bz2_file)

da = datetime.fromtimestamp(last_modified_time).strftime("%Y-%m-%d")
print(da)
