import bz2
import codecs
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dump.memory import print_memory
from labels.read_dump import filename, va_dir

time_start = time.time()
core_dir = str(Path(__file__)).replace('\\', '/').split("/dump/", maxsplit=1)[0]
Dump_Dir = "/data/project/himo/dumps"
test_limit = {1: 15000}
cc = {1: 0}
tt = {1: time.time()}
tab = {
    "delta": 0,
    "done": 0,
    "file_date": '',
    "All_items": 0,
    "langs": {},
}

def dump_it(tab):
    if 'nodump' in sys.argv:
        return
    jsonname = f"{Dump_Dir}/labels.json"
    if 'test' in sys.argv:
        jsonname = f"{Dump_Dir}/labels_test.json"
    with open(jsonname, "w", encoding='utf-8') as outfile:
        json.dump(tab, outfile)
    print("dump_it done")

def do_line(line):
    line = line.strip("\n").strip(",")
    tab['done'] += 1
    if 'pp' in sys.argv:
        print(line)
    if line.startswith("{") and line.endswith("}"):
        tab['All_items'] += 1
        cc[1] += 1
        json1 = json.loads(line)
        tats = ['labels', 'descriptions', 'aliases']
        for x in tats:
            for code in json1.get(x, {}):
                if code not in tab['langs']:
                    tab['langs'][code] = {'labels': 0, 'descriptions': 0, 'aliases': 0}
                tab['langs'][code][x] += 1
        del json1

def get_file_info(file_path):
    last_modified_time = os.path.getmtime(file_path)
    return datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d')

def check_file_date(file_date):
    with codecs.open(f"{va_dir}/file_date.txt", "r", encoding='utf-8') as outfile:
        old_date = outfile.read()
    if old_date == file_date and 'test' not in sys.argv and 'test1' not in sys.argv:
        print(f"file_date: {file_date} <<lightred>> unchanged")
        sys.exit(0)

def read_lines():
    print("def read_lines():")
    with bz2.open(filename, "rt", encoding="utf-8") as f:
        for line in f:
            do_line(line)
            if cc[1] % 100000 == 0:
                print(cc[1], time.time() - tt[1])
                tt[1] = time.time()
                print_memory()
            if cc[1] % 1000000 == 0:
                dump_it(tab)

def read_lines_test():
    print("def read_lines_test():")
    with bz2.open(filename, "rt", encoding="utf-8") as f:
        for line in f:
            do_line(line)
            if cc[1] % 100 == 0:
                print(f'cc[1]:{cc[1]}')
                print(f"done:{tab['done']}")
                print(cc[1], time.time() - tt[1])
                tt[1] = time.time()
                print_memory()
            if cc[1] > test_limit[1]:
                print('cc[1]>test_limit[1]')
                break

def read_file():
    print(f"read_file: read file: {filename}")
    if not os.path.isfile(filename):
        print(f"file {filename} <<lightred>> not found")
        return {}
    tab['file_date'] = get_file_info(filename)
    print(f"file date: {tab['file_date']}")
    print(f"file {filename} found, read it:")
    check_file_date(tab['file_date'])
    if 'test' in sys.argv:
        read_lines_test()
    else:
        read_lines()
    print(f"read all lines: {tab['done']}")
    end = time.time()
    delta = int(end - time_start)
    tab['delta'] = f'{delta:,}'
    print(f"read_file: done in {tab['delta']}")
    dump_it(tab)
    if 'test' not in sys.argv and 'nodump' not in sys.argv:
        with codecs.open(f"{va_dir}/file_date.txt", "w", encoding='utf-8') as outfile:
            outfile.write(tab['file_date'])

if __name__ == "__main__":
    read_file()
