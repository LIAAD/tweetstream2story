# gather corpus stats
import os
import sys

from pathlib import Path

from nltk import word_tokenize

def count_tokens(fd):
    return len(word_tokenize(fd.read()))

def count_elements(fd, element_type):

    count = 0
    for line in fd:
        if line[0] == "T":
            elements = line.split()
            if elements[1] == element_type:
                count += 1

    return count


def build_stats():

    data_dir = os.environ.get("DATA_DIR")

    if data_dir is None:
        print("Please, set DATA_DIR enviroment variable.")
        sys.exit(0)

    counts = {"tokens":[],"events":[],"participants":[],"time":[]}

    for dirpath, dirnames, filenames in os.walk(data_dir):
        for f in filenames:
            if f.endswith(".ann"):

                full_name = os.path.join(dirpath, f)
                p = Path(f)
                txt_file = os.path.join(data_dir,p.stem + ".txt")

                with open(txt_file, "r") as fd:
                    counts["tokens"].append(count_tokens(fd))

                with open(full_name, "r") as fd:
                    counts["events"].append(count_elements(fd, "Event"))

                with open(full_name, "r") as fd:

                    counts["participants"].append(count_elements(fd, "Participant"))
                with open(full_name, "r") as fd:
                    counts["time"].append(count_elements(fd, "Time"))

    print("Total #tokens:", sum(counts["tokens"]))
    print("Average #tokens:", sum(counts["tokens"])/len(counts["tokens"]))
    print("Total #events:", sum(counts["events"]))
    print("Total #participants:", sum(counts["participants"]))
    print("Total #time:", sum(counts["time"]))

if __name__ == "__main__":
    build_stats()
