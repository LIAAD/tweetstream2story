import os
import sys
from pathlib import Path

from . import read
from . import token_corpus

import spacy
import re

# regular expression of an integer number
NUMBER_RE = re.compile("^[0-9]*[1-9][0-9]*$")


class ReadBrat(read.Read):
    """
      Reader to brat file annotations and their text files
    """

    def __init__(self):
        """
        Load spacy model to read process brat files. Also
        store the files processed.
        """

        self.nlp = spacy.load("pt_core_news_lg")
        self.file_lst = []

    def toColumn(self, data_dir, output_dir):
        """
        Convert a set of files to column format, similar to Conll

        @param string: path of data to gather and process
        @param string: path of the ouput directory

        @return None
        """

        for dirpath, dirnames, filenames in os.walk(data_dir):
            for f in filenames:
                if f.endswith(".ann"):
                    p = Path(f)
                    fullname = os.path.join(data_dir, p.stem)
                    output_file = os.path.join(output_dir, "%s.conll" % p.stem)
                    self.fileToColumnFormat(fullname, output_file)

    def _is_adjacent_offset(self, i1, i2):
        """
        test if two intervals are adjacent

        @param (int,int): a tuple of integers
        @param (int,int): a tuple of integers

        @return int: 1 if i1 is adjacent, but before i2, -1 if i1 is adjacent
        , but after i2, and 0 otherwise
        """

        s1, e1 = i1
        s2, e2 = i2

        # if the interval i1 is adjacent, but it is placed before
        # the interval i2
        if e1 + 1 == s2:
            return 1
        elif e2 + 1 == s1:
            # if the interval i1 is adjacent, but it is placed after
            # the interval i2
            return -1
        else:
            return 0

    def _get_left_span(self, ann):
        """
        Given an annotation element (dictionary), it takes the left most span interval,

        """

        # (start, end)
        return (ann["offset1"][0], ann["offset1"][1])

    def _get_right_span(self, ann):
        """
        Given an annotation element (dictionary), it takes the right most span interval,

        """
        if "offset2" in ann:
            return (ann["offset2"][0], ann["offset2"][1])
        else:
            return (ann["offset1"][0], ann["offset1"][1])

    def _is_adjacent(self, el1, el2):
        """
        Check if two annotation elements (dictionaries) are adjacent to each other
        1, if el1 < el2, -1, if el1 > el2, and 0 if el1 is not adjacent to el2
        """

        if "offset2_start" in el1 and "offset2_start" in el2:
            return 0

        (left1_start, left1_end) = self._get_left_span(el1)
        (left2_start, left2_end) = self._get_left_span(el2)

        (right1_start, right1_end) = self._get_right_span(el1)
        (right2_start, right2_end) = self._get_right_span(el2)

        ans = self._is_adjacent_offset((left1_start, left1_end), (left2_start, left2_end))
        if ans != 0: return ans

        ans = self._is_adjacent_offset((left1_start, left1_end), (right2_start, right2_end))
        if ans != 0: return ans

        ans = self._is_adjacent_offset((right1_start, right1_end), (left2_start, left2_end))
        if ans != 0: return ans

        ans = self._is_adjacent_offset((right1_start, right1_end), (right2_start, right2_end))
        if ans != 0: return ans

        return 0

    def _build_merged_element(self, el1, el2):

        new_el = {}
        if "offset2_start" in el1:

            new_el["offset1"] = (el1["offset1"][0], el1["offset1"][1])

            # the union if make in the second offset
            new_el["offset2"] = (el1["offset2"][0], el2["offset2"][1])

        else:
            # the union if make in the first offset
            new_el["offset1"] = (el1["offset1"][0], el2["offset1"][1])
            if "offset2" in el2:
                new_el["offset2"] = (el2["offset2"][0], el2["offset2_end"][1])

        new_el["value"] = el1["value"] + " " + el2["value"]
        return new_el

    def merge_span(self, ann_entity):
        """
        It merge spans of annotations

        @param [dict]: a list of annotations as dictionaries

        @param [dict]:a list of annotations as dictionaries that were merged
        if they are in the same span text
        """

        # TODO: a recursive solution will be more suitable solution

        new_ann_type = []
        merged_indexes = []  # register elements that were already merged

        for idx_el, el in enumerate(ann_entity):

            # search for an element that is inside the
            # current span or contains the current span
            ans = 0
            for idx in range(idx_el + 1, len(ann_entity)):

                ans = self._is_adjacent(el, ann_entity[idx])

                if ans > 0:
                    new_el = self._build_merged_element(el, ann_entity[idx])
                    new_ann_type.append(new_el)
                    merged_indexes.append(idx)
                    break
                elif ans < 0:
                    new_el = self._build_merged_element(ann_entity[idx], el)
                    new_ann_type.append(new_el)
                    merged_indexes.append(idx)
                    break

            if ans == 0:
                if idx_el not in merged_indexes:
                    new_ann_type.append(el)

        return new_ann_type

    def merge_entity_span(self, ann):
        """
        Given a dictionary returned by read_annotation_file method,
        it merge span of entities

        @param dict: a dictionary of different entities that contains their
        annotation

        @return dict: a dictionary of different entities that contains their
        annotation merged if they are in the same text span
        """

        new_ann = {}
        for ent_type in ann:
            new_ann_ent = self.merge_span(ann[ent_type])
            new_ann[ent_type] = new_ann_ent

        return new_ann

    def read_annotation_file(self, file_ann):
        """
        It reads only the annotation file, then returns
        the processed tokens as TokenCorpus type

        @param string: path of data to gather and process

        @return dictionary: a dictionary of annotations
        """

        ann = {"Event": [], "Actor": [], "Time": [], "TIME_X3": [], \
               "ACTOR": [], "Participant": []}

        with open(file_ann, "r") as fd:
            for line in fd:
                ann_type = None
                if line[0] != '#' and line[0] == 'T':

                    line_toks = line.split()
                    ann_type = line_toks[1]

                    if ann_type not in ann:
                        ann[ann_type] = []

                    if ';' in line_toks[3]:
                        # this situation is when the annotation of th event
                        # is two segments not adjacents
                        offset1_start = int(line_toks[2])
                        offset1_end = int(line_toks[4])

                        offset2 = line_toks[3].split(';')
                        offset2_start = int(offset2[0])
                        offset2_end = int(offset2[1])

                        value = " ".join(line_toks[5:])

                        ann[ann_type].append({"offset1": (offset1_start, offset1_end), \
                                              "offset2": (offset2_start, offset2_end), \
                                              "value": value})

                    else:
                        offset1_start = int(line_toks[2])
                        offset1_end = int(line_toks[3])

                        value = " ".join(line_toks[4:])

                        ann[ann_type].append({"offset1": (offset1_start, offset1_end), \
                                              "value": value})
                # elif line[0] == 'A': # for now ignore attributes
                #    ref = line[2]
                #    if ref in ann_ref:
                #        ann_ref[ref][1].append((line[1], line[3))
        return self.merge_entity_span(ann)
        # return ann

    def process(self, data_dir):
        """
        It reads a set of files of annotations and text, then returns 
        the processed tokens as TokenCorpus type

        @param string: path of data to gather and process

        @return [[TokenCorpus]]: a list of lists of tokens
        """
        # process the data corpus
        # and return a list of tokens

        data_tokens = []

        for dirpath, dirnames, filenames in os.walk(data_dir):
            for f in filenames:
                if f.endswith(".ann"):

                    p = Path(f)
                    fullname = os.path.join(data_dir, p.stem)
                    token_lst = self.process_file(fullname)
                    self.file_lst.append(fullname + ".txt")

                    if len(token_lst) > 0:
                        data_tokens.append(token_lst)

        return data_tokens

    def process_file(self, data_file):
        """
        It reads only one file of annotation and text, then returns 
        the processed tokens as TokenCorpus type

        @param string: path of data to gather and process

        @return [TokenCorpus]: a list of tokens
        """

        file_ann = "%s.ann" % data_file
        file_txt = "%s.txt" % data_file

        token_lst = []
        if not os.path.exists(file_txt) or not os.path.exists(file_ann):
            return token_lst

        ann = {}  # the index is the offset of the annotation
        ann_ref = {}  # annotation by reference

        with open(file_ann, "r") as fd:
            for line in fd:
                # TODO: currently only read event annotations
                if line[0] != '#' and line[0] == 'T':

                    line_toks = line.split()
                    # ann[offset start] = (ref, ann_type, value_str)
                    if ';' in line_toks[3]:
                        # this situation is when the annotation of th event
                        # is two segments not adjacents
                        tmp = line_toks[3].split(';')
                        ann[(int(line_toks[2]), int(tmp[0]))] = (line_toks[0], line_toks[1], line_toks[5:])
                        ann[(int(tmp[1]), int(line_toks[4]))] = (line_toks[0], line_toks[1], line_toks[5:])
                        ann_ref[line[0]] = (
                            [(int(line_toks[2]), int(tmp[0])), (int(tmp[1]), int(line_toks[4]))], [])
                    else:
                        if NUMBER_RE.match(line_toks[2]):
                            ann[(int(line_toks[2]), int(line_toks[3]))] = (
                                line_toks[0], line_toks[1], line_toks[4:])
                            ann_ref[line[0]] = ([(int(line_toks[2]), int(line_toks[3]))], [])
                elif line[0] == 'A':
                    ref = line[2]
                    if ref in ann_ref:
                        ann_ref[ref][1].append((line[1], line[3]))

        idx_lst = ann.keys()

        idx_lst = sorted(idx_lst, key=lambda elem: elem[0])

        with open(file_txt, "r") as fd:

            doc = self.nlp(fd.read())
            count = 0

            for tok in doc:

                mytok = token_corpus.TokenCorpus()
                mytok.id = count
                mytok.text = tok.text
                mytok.lemma = tok.lemma_
                mytok.pos = tok.pos_
                mytok.dep = tok.dep_
                mytok.head = tok.head.text
                mytok.head_pos = tok.head.pos_
                mytok.head_lemma = tok.head.lemma_
                mytok.offset = tok.idx

                ans = self.search_idx(tok.idx, idx_lst)
                if ans != -1:
                    # annotations in token
                    (t0, t1) = idx_lst[ans]
                    ref, ann_type, _ = ann[(t0, t1)]

                    # TODO: more detail of the annotation in ann_ref

                    mytok.ann = ann_type

                token_lst.append(mytok)

                count += 1

        return token_lst

    def search_idx(self, idx, idx_lst):
        """
        it searches for tuples (t0, t1) in idx_lst where idx >= t0 and idx <= t1

        @param integer: an index
        @param [(integer,integer)]: a list of index

        @return integer: the position of the tuple or -1 if none is found
        """

        b = 0
        e = len(idx_lst) - 1

        m = int((b + e) / 2)
        pos = -1

        while b <= e:
            (t0, t1) = idx_lst[m]

            if idx == t0:
                pos = m
                break
            elif idx > t0:
                if idx > t1:
                    b = m + 1
                else:
                    pos = m
                    break
            else:
                e = m - 1

            m = int((b + e) / 2)

        return pos

    def __process_annotations(self, file_ann, ann, ann_ref):
        pass

    def fileToColumnFormat(self, ann_file, output_file):
        """
        Convert only one file to the column format.

        @param string: path of annotation file
        @param string: path of output file

        @return None
        """
        print("Processing %s..." % ann_file)

        tok_lst = self.process_file(ann_file)
        with open(output_file, "w") as fd:

            for tok in tok_lst:

                if tok.ann == 'Event':
                    ann = 'I'
                else:
                    ann = 'O'

                fd.write("%d %s %s %s\n" % (tok.id, tok.text.strip(), tok.pos, ann))
        print("Output %s" % output_file)


if __name__ == "__main__":
    # only to unit  tests
    data_dir = os.environ.get("DATA_DIR")
    output_dir = os.environ.get("COLUMN_DIR")

    if data_dir is None:
        print("Please, set DATA_DIR enviroment variable.")
        sys.exit(0)
    if output_dir is None:
        print("Please, set COLUMN_DIR enviroment variable.")
        sys.exit(0)

    r = ReadBrat()
    # r.process(data_dir) # read and return a list of list of tokens
    r.toColumn(data_dir, output_dir)
