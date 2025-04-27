#!/bin/bash

wget https://raw.githubusercontent.com/WikiAr/WikiData-Dumps/refs/heads/update/dump26/most_props.py -O most_props.py

wget https://raw.githubusercontent.com/WikiAr/WikiData-Dumps/refs/heads/update/dump26/Web.py -O Web.py

wget https://raw.githubusercontent.com/WikiAr/WikiData-Dumps/refs/heads/update/requirements.in -O requirements.in

pip install -r requirements.in
# nix-shell -p python311Packages.pip
python3 most_props.py

python3 Web.py

echo "Finishing dump26..."
