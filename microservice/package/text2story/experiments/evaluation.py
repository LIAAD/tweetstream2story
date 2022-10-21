import os

from pathlib import Path

import text2story as t2s  # Import the package
from text2story.readers import read_brat

import argparse


def start():
    t2s.start()  # Load the pipelines


##########################
### Auxiliary methods ####
##########################

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def partial_match(b1, e1, b2, e2):
    """
    Check if the interval (b1,e1) intersects
    with the interval (b2, e2)

    @param int: beginning of a interval
    @param int: ending of a interval
    @param int: beginning of a interval
    @param int: ending of a interval

    @return bool: if there is an intersection between an interval
     it returns true, otherwise returns false
    """

    if (b2 <= e1) and (b2 >= b1):
        return True
    if (e2 <= e1) and (e2 >= b1):
        return True

    if (b1 >= b2) and (e1 <= e2):
        return True
    return False


def partial_search_annotation(ann, ann_lst):
    """
    given  an annotation (dictionary), do a binary search in a list of annotations
    if the tokens are in the annotation list. The search looks for only
    if there is in intersection between ann and any of the intervals in
    ann_lst

    @param (int, int): a tuple of integers that indicates an intervals
    @param [(int,int)]: a list of intervals

    @return int: return a integer that is the index position of the element, or -1
    if the interval is absence of ann_lst

    """

    ans = -1
    # ans = len(word_tokenize(ann["value"]))
    start, end = ann["offset1"]
    b = 0
    e = len(ann_lst) - 1
    m = int((b + e) / 2)

    while (b <= e):
        start_search, end_search = ann_lst[m]

        if end < start_search:
            e = m - 1
            m = int((b + e) / 2)
        else:
            if start > end_search:
                b = m + 1
                m = int((b + e) / 2)
            else:
                if partial_match(start, end, start_search, end_search):
                    ans = m
                    break

    return ans


def search_annotation(ann, ann_lst):
    """
    given  an annotation (dictionary), do a binary search in a list of annotations
    if the tokens are in the annotation list

    @param (int, int): a tuple of integers that indicates an intervals
    @param [(int,int)]: a list of intervals

    @return int: return a integer that is the index position of the element, or -1
    if the interval is absence of ann_lst
    """

    ans = -1
    # ans = len(word_tokenize(ann["value"]))
    start, end = ann["offset1"]
    b = 0
    e = len(ann_lst) - 1
    m = int((b + e) / 2)

    while (b <= e):
        start_search, end_search = ann_lst[m]

        if end < start_search:
            e = m - 1
            m = int((b + e) / 2)
        else:
            if start > end_search:
                b = m + 1
                m = int((b + e) / 2)
            else:
                if start == start_search and end == end_search:
                    ans = m
                break

    return ans


def get_intervals(ann_lst):
    """
    get the intervals of annotations as a sorted tuple list

    @param dictionary: dictionary of annotations

    @return tuple list of integers
    """

    interval_lst = []
    for el in ann_lst:
        interval_lst.append(el["offset1"])
        if "offset2" in el:
            interval_lst.append(el["offset2"])

    sorted(interval_lst, key=lambda elem: elem[0])

    return interval_lst


def compute_relax_scores(ann_pred, ann_target):
    """
    it computes the  relaxed scores (tokens in common is a match)
    for two annotations

    @param dictionary: annotations of the prediction
    @param dictionary: annotations of the target/human-labeled

    @return dictionary: scores (precision, recall, and f1)
    computed in a strict manner
    """

    interval_pred_lst = get_intervals(ann_pred)
    interval_target_lst = get_intervals(ann_target)

    tp = 0  # true positive
    fp = 0  # false positive

    for pred in ann_pred:
        ans = partial_search_annotation(pred, interval_target_lst)
        if ans != -1:
            # ann_target
            tp += 1  # true positive
        else:
            # false positive
            fp += 1

    fn = 0  # false negative
    for target in ann_target:
        ans = partial_search_annotation(target, interval_pred_lst)
        if ans == -1:
            fn += 1

    try:
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * (precision * recall) / (precision + recall)
    except ZeroDivisionError:
        precision = 0
        recall = 0
        f1 = 0
        print(ann_target)
        print(ann_pred)
        print("compute_relax_scores: Error in compute scores")

    return {"precision": precision, "recall": recall, "f1": f1}


def compute_strict_scores(ann_pred, ann_target):
    """
    it computes the strict scores for two annotations

    @param dictionary: annotations of the prediction
    @param dictionary: annotations of the target/human-labeled

    @return dictionary: scores (precision, recall, and f1)
    computed in a strict manner
    """

    interval_pred_lst = get_intervals(ann_pred)
    interval_target_lst = get_intervals(ann_target)

    tp = 0  # true positive
    fp = 0  # false positive

    for pred in ann_pred:
        ans = search_annotation(pred, interval_target_lst)
        if ans != -1:
            # ann_target
            tp += 1  # true positive
        else:
            # false positive
            fp += 1

    fn = 0  # false negative
    for target in ann_target:
        ans = search_annotation(target, interval_pred_lst)
        if ans == -1:
            fn += 1

    try:
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * (precision * recall) / (precision + recall)
    except ZeroDivisionError:
        precision = 0
        recall = 0
        f1 = 0
        print(ann_target)
        print(ann_pred)
        print("compute_strict_scores: Error in compute scores")

    return {"precision": precision, "recall": recall, "f1": f1}


#########################################
### Prediction and evaluation methods ###
#########################################

def extract_element(doc, el, tool):
    """
    It extracts a given element (participant, event or time) using a given
    tool.

    @param doc: a Narrative object
    @param string: a string specifying the type of element to be extracted
    @param string: a string specifying the type of tool to apply in the document

    @return None
    """

    if el == 'participant':
        doc.extract_actors(tool)
    elif el == 'event':
        doc.extract_events(tool)
    elif el == 'time':
        doc.extract_times(tool)
    else:
        raise Exception("extract_element: Unrecognize element %s" % el)


def evaluate_element(pred_file, target_file, el):
    """
    It evaluates a given element (participant, event or time) .

    @param string: path of prediction file (.ann)
    @param string: path of target annotated file (.ann)
    @param string: a string specifying the type of elment to evaluate

    @return (dict, dict) the relaxed and strict results
    """

    if el == 'participant':
        return evaluate_actor(pred_file, target_file)
    elif el == 'event':
        return evaluate_event(pred_file, target_file)
    elif el == 'time':
        return evaluate_time(pred_file, target_file)
    else:
        raise Exception("evaluate_element: Unrecognize element %s" % el)


def evaluate_event(pred_file, target_file):
    """
    Implements token event precision/recall/f1 and span event precision/recall/f1

    @param string: predict file in the brat .ann format
    @param string: target file (human labeled) in the brat .ann format

    @return a tuple of dictionaries
    """

    reader = read_brat.ReadBrat()

    ann_pred = reader.read_annotation_file(pred_file)
    ann_target = reader.read_annotation_file(target_file)

    # compute accuracy of the exacttly same span
    event_pred = ann_pred["Event"]
    event_target = ann_target["Event"]

    scores_relax = compute_relax_scores(event_pred, event_target)
    scores = compute_strict_scores(event_pred, event_target)
    return scores_relax, scores


def evaluate_actor(pred_file, target_file):
    """
    Implements token actor precision/recall/f1 and span actor precision/recall/f1

    @param string: predict file in the brat .ann format
    @param string: target file (human labeled) in the brat .ann format

    @return a tuple of dictionaries
    """

    reader = read_brat.ReadBrat()

    ann_pred = reader.read_annotation_file(pred_file)
    ann_target = reader.read_annotation_file(target_file)

    # compute accuracy of the exacttly same span

    actor_pred = ann_pred["Actor"]
    # conditions to preserve compatibility between anotation versions
    if len(actor_pred) == 0:
        actor_pred = ann_pred["ACTOR"]
    if len(actor_pred) == 0:
        actor_pred = ann_pred["Participant"]

    actor_target = ann_target["Actor"]
    if len(actor_target) == 0:
        actor_target = ann_target["ACTOR"]
    if len(actor_target) == 0:
        actor_target = ann_target["Participant"]

    scores_relax = compute_relax_scores(actor_pred, actor_target)
    scores = compute_strict_scores(actor_pred, actor_target)
    return scores_relax, scores


def evaluate_time(pred_file, target_file):
    """
    Implements token time precision/recall/f1 and span time precision/recall/f1

    @param string: predict file in the brat .ann format
    @param string: target file (human labeled) in the brat .ann format

    @return a tuple of dictionaries
    """

    reader = read_brat.ReadBrat()
    ann_pred = reader.read_annotation_file(pred_file)
    ann_target = reader.read_annotation_file(target_file)

    # compute accuracy of the exacttly same span
    time_pred = ann_pred["Time"]
    if len(time_pred) == 0:
        time_pred = ann_pred["TIME_X3"]
    time_target = ann_target["Time"]

    scores_relax = compute_relax_scores(time_pred, time_target)
    scores = compute_strict_scores(time_pred, time_target)
    return scores_relax, scores


def prediction(input_dir, results_dir, el, tool, language):
    """
    Read brat data (.ann and .txt files) in the input directory,
    and write the results (columns files: token, pred_label, target_label)
    in the results dir

    @param string: input directory with ann and txt files
    @param string: directory with results file for each document file in
    the input_dir

    @return [(string,string)]: a tuple file list to compare
    """

    reader = read_brat.ReadBrat()

    doc_lst = reader.process(input_dir)

    doc_pred_target = []  #

    for idx_doc, doc in enumerate(doc_lst):
        text_ = ""
        with open(reader.file_lst[idx_doc], "r") as fd:
            text_ = fd.read()

        narrative_doc = t2s.Narrative(language, text_, "2020-10-11")

        el_result_dir = os.path.join(results_dir, el)

        if not (os.path.exists(el_result_dir)):
            os.mkdir(el_result_dir)

        tool_result_dir = os.path.join(el_result_dir, tool)

        if not (os.path.exists(tool_result_dir)):
            os.mkdir(tool_result_dir)

        # extract the element in the given tool
        print("%s extracting from file %s" % (tool, reader.file_lst[idx_doc]))
        extract_element(narrative_doc, el, tool)

        ann_filename = os.path.basename(reader.file_lst[idx_doc])
        ann_filename = os.path.join(tool_result_dir, ann_filename)

        iso_str = narrative_doc.ISO_annotation()
        with open(ann_filename, "w") as fd:
            fd.write(iso_str)

        target_file = Path(reader.file_lst[idx_doc]).stem + ".ann"
        target_file = os.path.join(input_dir, target_file)

        doc_pred_target.append((ann_filename, target_file))

    return doc_pred_target


def process_evaluation(element, doc_lst):
    """
    Process evaluation for a given element (time, actors or event), in a
    given tool (spacy, spacy, py_heideltime, custompt, etc).

    You should set DATA_DIR and RESULTS_DIR in your PATH enviroment
    vari

    @param string: the element to be extracted
    @param string: the annotator tool to be employed in the extraction

    @param dictionary: a dictionary with the results
    """

    res = {"precision_relax": [], "recall_relax": [], "f1_relax": [], "precision": [], "recall": [], "f1": []}

    for pred_file, target_file in doc_lst:
        print("Evaluating %s and %s" % (pred_file, target_file))
        scores_relax, scores = evaluate_element(pred_file, target_file, element)

        res["precision_relax"].append(scores_relax["precision"])
        res["recall_relax"].append(scores_relax["recall"])
        res["f1_relax"].append(scores_relax["f1"])

        res["precision"].append(scores["precision"])
        res["recall"].append(scores["recall"])
        res["f1"].append(scores["f1"])

    return res


def build_evaluation(narrative_elements, language, data_dir: str, results_dir: str):
    """
    Process the evaluation of DATA_DIR (enviroment variable) and put
    the extracted elements in the RESULTS_DIR (enviroment variable)

    @param dict: A dictionary with the elements (actor, time, event) with the
    the tool list to be employed
    @param string: the language to be evaluated (pt or en)
    @param: The System Path where data is stored
    @parm: The System Path where results will be output
    @return None
    """
    res = {}

    for el in narrative_elements:
        doc_pred_lst = prediction(data_dir, results_dir, el, narrative_elements[el], language)
        res[el] = process_evaluation(el, doc_pred_lst)

    return res


def print_metrics_result(res: dict):
    print(f"\n-------Metrics Results-------")

    for key_tool in res.keys():
        for key_metric in res[key_tool].keys():
            avg_value = calculate_average_result(res[key_tool][key_metric])
            print(f"Average Value for Metric {key_metric} using tool{key_tool} is: {avg_value}")


def calculate_average_result(result) -> float:
    counter = 0

    for elem in result:
        counter += elem / len(result)

    return counter


def main(narrative_elements: dict, language: str, data_dir: str = None, results_dir: str = None):

    start()

    res = build_evaluation(narrative_elements=narrative_elements, language=language, data_dir=data_dir,
                           results_dir=results_dir)

    print_metrics_result(res)

if __name__ == "__main__":

    my_parser = argparse.ArgumentParser(description='Evaluation of a give dataset according to standard metrics')

    my_parser.add_argument("inputdir", action='store', type=dir_path, help="The directory that contains the target files (brat format) and the txt narrative files.")
    my_parser.add_argument("resultsdir", action='store', type=dir_path, help="The directory where are the files with the extracted entities.")

    my_parser.add_argument("--language", action='store', type=str, help="Current support en (English) and pt (Portuguese. Default: en.")

    my_parser.add_argument("--participant", action='store', type=str, help="The tools to extract participants from narratives. Default: spacy.")
    my_parser.add_argument("--time", action='store', type=str, help="The tools to extract time from narratives. Default: py_heideltime.")
    my_parser.add_argument("--event", action='store', type=str, help="The tools to extract event from narratives. Default: allennlp.")

    args = my_parser.parse_args()

    language = 'en'
    if args.language is not None:
        if args.language != 'en' and args.language != 'pt':
            print("Language option not recognized: %s." % args.language)
            sys.exit()
        language = args.language

    participant_tool = 'spacy'
    if args.participant is not None:
        if args.participant not in t2s.participant_tool_names():
            print("Participant tool not recognized: %s." % args.participant)
            sys.exit()
        participant_tool = args.participant

    time_tool = 'py_heideltime'
    if args.time is not None:
        if args.time not in t2s.time_tool_names():
            print("Time tool not recognized: %s." % args.time)
            sys.exit()
        time_tool = args.time

    event_tool = 'allennlp'
    if args.event is not None:
        if args.event not in t2s.event_tool_names():
            print("Event tool not recognized: %s." % args.event)
            sys.exit()
        event_tool = args.event

    narrative_elements = {"participant":participant_tool,\
                          "time":time_tool,\
                          "event":event_tool}

    main(narrative_elements, language,\
            args.inputdir, args.resultsdir)
     
     
     

