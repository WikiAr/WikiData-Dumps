
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/WikiAr/WikiData-Dumps)


# WikiData Dumps Processing Scripts

This repository contains scripts used for processing WikiData dumps, specifically for the "claims" and "labels" data.

## Claims Package

The claims package includes scripts for processing claims data from WikiData dumps. The main functionalities include:

- Parsing claims data from the WikiData dump.
- Generating statistics and reports on the usage of properties within the claims.
- Saving the processed data and statistics in a structured format.

### Key Scripts

- `do_text.py`: Processes the claims data and generates a textual report.
- `read_dump.py`: Reads and parses the claims data from the WikiData dump.
- `save.py`: Saves the processed claims data to a specified location.

## Labels Package

The labels package consists of scripts for handling labels data from WikiData dumps. The primary features are:

- Reading labels data from the WikiData dump.
- Creating reports on the number of labels, descriptions, and aliases for items per language.
- Outputting the results in a structured format for further analysis.

### Key Scripts

- `do_text.py`: Generates a text report based on the labels data.
- `read_dump.py`: Reads and processes the labels data from the WikiData dump.
- `save.py`: Saves the processed labels data to a designated location.

### Reports links
* https://www.wikidata.org/wiki/User:Mr._Ibrahem/claims
* https://www.wikidata.org/wiki/User:Mr._Ibrahem/p31
* https://www.wikidata.org/wiki/User:Mr._Ibrahem/Language_statistics_for_items
* https://www.wikidata.org/wiki/Template:Tr_langcodes_counts
* https://ar.wikipedia.org/wiki/ويكيبيديا:مشروع_ويكي_بيانات/تقرير_P31
