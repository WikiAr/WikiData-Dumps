import os
import bz2
import tqdm
from humanize import naturalsize

from datetime import datetime

bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"

file_size = os.path.getsize(bz2_file)

print(naturalsize(file_size, binary=True))

# Get the time of last modification
last_modified_time = os.path.getmtime(bz2_file)

da = datetime.fromtimestamp(last_modified_time).strftime("%Y-%m-%d")
print(da)
