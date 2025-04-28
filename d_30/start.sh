# sh start.sh
set -euo pipefail

wget https://raw.githubusercontent.com/WikiAr/WikiData-Dumps/refs/heads/update/d_30/most_props.py -O most_props.py
wget https://raw.githubusercontent.com/WikiAr/WikiData-Dumps/refs/heads/update/d_30/web2.py -O web2.py
wget https://raw.githubusercontent.com/WikiAr/WikiData-Dumps/refs/heads/update/d_30/requirements.in -O requirements.in

pip install -r requirements.in
python3 -m pip install -r requirements.in


python3 most_props.py

python3 web2.py from_url
