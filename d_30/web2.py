"""
https://hub-paws.wmcloud.org/user/Mr.%20Ibrahem/lab/tree/dump

tfj run dump2 --mem 1Gi --image python3.9 --command "$HOME/local/bin/python3 /data/project/himo/bots/dump_core/dump25/r_27.py"

current_count: 150000 time: 34.07094955444336
current_count: 162500 time: 32.720284938812256


python3 bots/dump_core/d_30/most_props.py
python3 bots/dump_core/d_30/web2.py

"""
import multiprocessing as mp
import os
import tqdm
import psutil
import gc
import json
import time
import sys
import bz2
import requests
from pathlib import Path
from humanize import naturalsize  # naturalsize(file_size, binary=True)


class HHH:
    def __init__(self, data, most_props, dump_file):
        self.most_data = {"q": "", "count": 0}
        self.time_start = time.time()
        self.Dir = Path(__file__).parent
        self.most_props = most_props
        self.data = data
        self.tt = time.time()

        # Initialize directories
        self.dump_dir_claims_fixed = self.Dir / "parts1_claims_fixed"
        self.dump_parts1_fixed = self.Dir / "parts1_fixed"
        # ---
        self.dump_file = dump_file

    def dump_lines_claims(self, linesc):
        """Process and dump claims data."""
        if not linesc:
            return

        # self.dump_done["claims"] += 1

        _line = {
            "qid": "Q00",
            "claims": {"P31": ["Q5", "Q0"]},
        }

        most = {"q": "", "count": 0}

        tabs = {
            "len_all_props": 0,
            "items_0_claims": 0,
            "items_1_claims": 0,
            "items_no_P31": 0,
            "All_items": 0,
            "total_claims": 0,
            "properties": {},
        }

        tabs["All_items"] += len(linesc)

        for line in linesc:
            claims = line.get("claims", {})
            _claims = {"P59": ["Q10519"], "P31": ["Q523", "Q67206691"], "P6259": ["Q1264450"]}

            claims_length = len(claims)

            if claims_length > most["count"]:
                most["count"] = claims_length
                most["q"] = line["qid"]

            if claims_length == 0:
                tabs["items_0_claims"] += 1
                continue

            if claims_length == 1:
                tabs["items_1_claims"] += 1

            if "P31" not in claims:
                tabs["items_no_P31"] += 1

            for pid, qids in claims.items():
                tabs["total_claims"] += len(qids)

                if pid not in tabs["properties"]:
                    tabs["properties"][pid] = {
                        "qids": {},
                        "items_use_it": 0,
                        "lenth_of_usage": 0,
                        "len_of_qids": 0,
                        "len_prop_claims": 0,
                    }

                tabs["properties"][pid]["lenth_of_usage"] += 1
                tabs["properties"][pid]["items_use_it"] += 1

                for qid in qids:
                    if qid not in tabs["properties"][pid]["qids"]:
                        tabs["properties"][pid]["qids"][qid] = 0
                    tabs["properties"][pid]["qids"][qid] += 1

            del claims, line

        if most["count"] > self.most_data["count"]:
            self.most_data = most

        items_file_fixed = self.dump_dir_claims_fixed / f"{self.dump_file}.json"

        with open(items_file_fixed, "w", encoding="utf-8") as f:
            json.dump(tabs, f)

        items_file_fixed_size = naturalsize(os.path.getsize(items_file_fixed), binary=True)
        print(f"dump_lines_claims fixed: {items_file_fixed_size}")

    def dump_lines(self, linesx):
        """Process and dump main data lines."""
        if not linesx:
            return

        # self.dump_done[1] += 1

        tab = {
            "no": {
                "labels": 0,
                "descriptions": 0,
                "aliases": 0,
                "sitelinks": 0,
            },
            "most": {
                "labels": {"q": "", "count": 0},
                "descriptions": {"q": "", "count": 0},
                "aliases": {"q": "", "count": 0},
                "sitelinks": {"q": "", "count": 0},
            },
            "All_items": 0,
            "sitelinks": {},
            "langs": {},
        }

        tab["All_items"] += len(linesx)

        _json1 = {
            "labels": ["el", "ay"],
            "aliases": ["el", "ay"],
            "descriptions": ["cy", "sk", "mk", "vls"],
            "sitelinks": ["arwiki", "enwiki", "mk", "vls"],
        }

        tats = ["labels", "descriptions", "aliases", "sitelinks"]

        for json1 in linesx:
            for x in tats:
                ta_o = json1.get(x, {})

                if len(ta_o) == 0:
                    tab["no"][x] += 1
                    continue

                if len(ta_o) > tab["most"][x]["count"]:
                    tab["most"][x]["count"] = len(ta_o)
                    tab["most"][x]["q"] = json1["qid"]

                for code in ta_o:
                    if x == "sitelinks":
                        if code not in tab["sitelinks"]:
                            tab["sitelinks"][code] = 0
                        tab["sitelinks"][code] += 1
                    else:
                        if code not in tab["langs"]:
                            tab["langs"][code] = {"labels": 0, "descriptions": 0, "aliases": 0}
                        tab["langs"][code][x] += 1

        file_fixed = self.dump_parts1_fixed / f"{self.dump_file}.json"

        with open(file_fixed, "w", encoding="utf-8") as f:
            json.dump(tab, f)

        fixed_size = naturalsize(os.path.getsize(file_fixed), binary=True)
        print(f"dump_lines fixed: {fixed_size}")

    def print_memory(self, i):
        """Print memory usage information."""
        now = time.time()
        print(f"current_count:{i:,}", "time:", now - self.tt)
        self.tt = now

        green, purple = "\033[92m%s\033[00m", "\033[95m%s\033[00m"
        usage = psutil.Process(os.getpid()).memory_info().rss
        usage = usage / 1024 // 1024
        delta = int(now - self.time_start)
        print(green % "Memory usage:", purple % f"{usage} MB", f"time: to now {delta}")

    def fix_property(self, pv):
        """Extract property values from claims."""
        return [claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
                for claim in pv
                if claim.get("mainsnak", {}).get("datatype", "") == "wikibase-item"]

    def filter_and_process(self, entity_dict):
        """Filter and process entity dictionary."""
        entity_dict = json.loads(entity_dict)
        if entity_dict["type"] == "item":
            claims = entity_dict.get("claims", {})
            line = {
                "qid": entity_dict["title"],
                "labels": list(entity_dict.get("labels", {}).keys()),
                "descriptions": list(entity_dict.get("descriptions", {}).keys()),
                "aliases": list(entity_dict.get("aliases", {}).keys()),
                "sitelinks": list(entity_dict.get("sitelinks", {}).keys()),
            }
            line2 = {
                "qid": entity_dict["title"],
                "claims": {p: self.fix_property(pv) for p, pv in claims.items() if p in self.most_props},
            }
            return line, line2
        return None, None

    def start(self):
        print("______________________________")
        print(f"start {len(self.data):,}")
        # ---
        mem_nu = len(self.data) // 4
        # ---
        lines = []
        lines_claims = []

        for i, entity in enumerate(self.data, start=1):
            line, line2 = self.filter_and_process(entity)
            if line:
                lines.append(line)
                lines_claims.append(line2)

            if i % mem_nu == 0 and "multi" not in sys.argv:
                self.print_memory(i)

        print(f"len self.data:{len(self.data):,}:")
        print(f"\t len lines:{len(lines):,}")
        print(f"\t len lines_claims:{len(lines_claims):,}")
        print(f"\t {self.dump_file=}")

        self.dump_lines(lines)
        self.dump_lines_claims(lines_claims)

        lines_claims.clear()
        lines.clear()
        gc.collect()

        self.print_memory(i)

        return self.most_data


class DumpProcessor():
    def __init__(self):
        self.time_start = time.time()
        self.Dir = Path(__file__).parent

        # Initialize directories
        self.dump_dir_claims_fixed = self.Dir / "parts1_claims_fixed"
        self.dump_parts1_fixed = self.Dir / "parts1_fixed"

        # Create directories if they don't exist
        self.check_dir(self.dump_dir_claims_fixed)
        self.check_dir(self.dump_parts1_fixed)

        self.mosts = []
        # Initialize counters
        self.dump_done = {1: 0, "claims": 0}
        self.done1_lines = self.Dir / "done1_lines.txt"

        # Initialize done file
        with open(self.done1_lines, "w", encoding="utf-8") as f:
            f.write("")

        # Initialize most claims data
        self.most_path = self.Dir / "most_claims.json"
        if not self.most_path.exists():
            self.most_path.write_text('{"q": "", "count": 0}')
        self.most_data = json.loads(self.most_path.read_text())

        # Load properties
        properties_path = self.Dir / "properties.json"
        with open(properties_path, "r", encoding="utf-8") as f:
            self.most_props = json.load(f)

    def parse_lines(self, bz2_file, max_lines=None):
        """Parse lines from a bz2 file."""
        print(f"Parsing lines from file: {bz2_file}")
        # ---
        line_count = 0  # Counter for the number of lines processed
        # ---
        with bz2.open(bz2_file, "r") as f:
            for line in f:
                line = line.decode("utf-8").strip("\n").strip(",")
                if line.startswith("{") and line.endswith("}"):
                    line_count += 1  # Increment the line counter
                    yield line
                    if max_lines and line_count >= max_lines:
                        print(f"Reached the maximum of {max_lines:,} lines. Stopping.")
                        return

    def parse_lines_from_url(self, url, max_lines=1_000_000):
        """Parse lines from a URL, but stop after processing a maximum number of lines."""
        print(f"Fetching data from URL: {url}")
        # ---
        session = requests.session()
        session.headers.update({"User-Agent": "Himo bot/1.0 (https://himo.toolforge.org/; tools.himo@toolforge.org)"})
        # ---
        with session.get(url, stream=True) as response:
            print("Response received. Checking status...")
            response.raise_for_status()

            decompressor = bz2.BZ2Decompressor()
            buffer = b""
            print(f"Starting to process chunks...:{max_lines=}")
            all_chunks = 0
            line_count = 0  # Counter for the number of lines processed

            for chunk in response.iter_content(chunk_size=1024 * 1024):
                all_chunks += 1
                if chunk:
                    buffer += decompressor.decompress(chunk)

                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        line = line.strip().strip(b',')

                        if line.startswith(b"{") and line.endswith(b"}"):
                            yield line.decode('utf-8')
                            line_count += 1  # Increment the line counter

                            # Stop processing if the maximum number of lines is reached
                            if max_lines and line_count >= max_lines:
                                print(f"Reached the maximum of {max_lines:,} lines. Stopping.")
                                return

            print(f"Total chunks processed: {all_chunks}")

            # Handle remaining data in buffer
            if buffer.strip().startswith(b"{") and buffer.strip().endswith(b"}"):
                yield buffer.decode('utf-8')
                line_count += 1

            print(f"Processed {line_count} lines in total.")

    def check_dir(self, path):
        """Check if directory exists, if not create it."""
        if not path.exists():
            path.mkdir()

    def dump_lines_new(self, data):
        self.dump_done[1] += 1

        bot = HHH(data, self.most_props, self.dump_done[1])

        most = bot.start()
        self.mosts.append(most)

        # if most["count"] > self.most_data["count"]:
        #     self.most_data = most
            # self.most_path.write_text(json.dumps(self.most_data))

    def dump_lines_new_multi(self, data_n):
        data, file = data_n

        bot = HHH(data, self.most_props, file)

        most = bot.start()
        self.mosts.append(most)

    def get_data(self, bz2_file, url):
        # time_start = time.time()
        # ---
        if "from_url" in sys.argv:
            print(f"Starting download and processing... {url}")
            data = self.parse_lines_from_url(url, max_lines=50_000)
        else:
            file_size = os.path.getsize(bz2_file)
            print(naturalsize(file_size, binary=True))
            data = self.parse_lines(bz2_file, max_lines=50_000)
        # ---
        # time_end = time.time()
        # delta = int(time_end - time_start)
        # # ---
        # print(f"get_data: Time taken: {delta} seconds, time.sleep(3)")
        # time.sleep(3)
        # ---
        return data

    def dump_batch(self, batch):
        """دالة لمعالجة دفعة كاملة."""
        for lines in batch:
            self.dump_lines_new_multi(lines)
        gc.collect()

    def process_data_new(self, bz2_file="", url=""):
        """Main processing method with batching and multiprocessing."""
        # dump_numbs = 100_000
        dump_numbs = 5_000
        batch_size = 2  # عدد القوائم التي تجمعها قبل إرسالها للمعالجة
        all_lines = []
        batches = []

        data = self.get_data(bz2_file, url)

        for i, entity_dict in enumerate(data, start=1):
            # ---
            all_lines.append(entity_dict)
            # ---
            if len(all_lines) == dump_numbs:
                self.dump_done[1] += 1
                # ---
                batches.append([all_lines, self.dump_done[1]])
                # ---
                all_lines = []
                # ---
                if len(batches) == batch_size:
                    print(f"Processing batch at line {i:,}")

                    with mp.Pool(processes=batch_size) as pool:
                        pool.map(self.dump_batch, [[batch] for batch in batches])

                    batches.clear()
                    gc.collect()

        # معالجة الباقي بعد الانتهاء
        if all_lines:
            self.dump_lines_new(all_lines)

        for most in self.mosts:
            if most["count"] > self.most_data["count"]:
                self.most_data = most

        self.most_path.write_text(json.dumps(self.most_data))

        print("Processing completed.")

    def process_data(self, bz2_file="", url=""):
        """Main processing method."""
        dump_numbs = 100000
        all_lines = []

        data = self.get_data(bz2_file, url)

        for i, entity_dict in enumerate(data, start=1):
            all_lines.append(entity_dict)

            if dump_numbs == len(all_lines) and all_lines:
                print(f"data line: {i:,}, len lines:{len(all_lines):,}")

                self.dump_lines_new(all_lines)

                all_lines.clear()
                gc.collect()

        print(f"process_data DONE: {i:,=}")

        if all_lines:
            self.dump_lines_new(all_lines)

        for most in self.mosts:
            if most["count"] > self.most_data["count"]:
                self.most_data = most

        self.most_path.write_text(json.dumps(self.most_data))

        print("Processing completed.")

    def main(self):
        """Entry point for the script."""
        bz2_file = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
        url = "https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2"
        # ---
        if "multi" in sys.argv:
            self.process_data_new(bz2_file=bz2_file, url=url)
        else:
            self.process_data(bz2_file=bz2_file, url=url)
        # ---
        end = time.time()
        delta = int(end - self.time_start)
        # ---
        print(f"read_file: done in {delta}")


if __name__ == "__main__":
    processor = DumpProcessor()
    processor.main()
