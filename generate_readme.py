import os

from claims.do_text import make_text
from claims.read_dump import read_file as read_claims
from labels.labels_old_values import make_old_values
from labels.read_dump import read_file as read_labels


def generate_readme():
    claims_data = read_claims()
    labels_data = read_labels()
    claims_text = make_text(claims_data)
    labels_text = make_old_values(labels_data)
    readme_text = claims_text + "\n" + labels_text
    with open("README.md", "w") as readme_file:
        readme_file.write(readme_text)

if __name__ == "__main__":
    generate_readme()
