"""
    A custom annotator for events in portuguese language

    The model is a random forest based on the lusa news labeled data
"""

# adding root directory
import sys

sys.path.insert(0, '..')
sys.path.insert(0, '../../')

"""
    A custom annotator for events in portuguese language

    The model is a random forest based on the lusa news labeled data
"""
import spacy
import joblib
import numpy as np
import pandas as pd

import os
# adding root directory
import sys

sys.path.insert(0, '..')
sys.path.insert(0, '../../')

from text2story.readers.token_corpus import TokenCorpus

from sklearn.ensemble import GradientBoostingClassifier

import nlpnet

pipeline = {}

# mapping of pos tag to a integer number
pos2idx = {"<S>": 1, "PROPN": 2, "PUNCT": 3, "NUM": 4, \
           "ADP": 5, "SPACE": 6, "DET": 7, "NOUN": 8, \
           "CCONJ": 9, "ADJ": 10, "VERB": 11, "ADV": 12, \
           "SCONJ": 13, "AUX": 14, "PRON": 15, "SYM": 16, \
           "X": 17}

# the size of the window to the
# features of the model, currently the model was trained with 2
WINDOW_SIZE = 2


def load():
    current_path = os.path.dirname(__file__)
    # pipeline["event_tagger"] = joblib.load(os.path.join(current_path, "gb_custom_event_pt.joblib"))
    pipeline["event_tagger"] = joblib.load(os.path.join(current_path, "crf_2.joblib"))
    pipeline["pos_tagger"] = spacy.load("pt_core_news_lg")
    pipeline["srl_tagger"] = nlpnet.SRLTagger(os.path.join(current_path, "srl-pt/"), language="pt")


def _get_data(idx_lst, all_ftrs):
    """
    it gets the data in all_ftr lst that has the index in the idx_lst

    @param [integer]: a list of index
    @param [[float]]: a list of lists of features
    """

    X = []
    y = []
    for i in idx_lst:
        for data in all_ftrs[i]:
            y.append(data[-1])

            # concat all the tokens in only one vector
            X.append(data[:-1])

    return np.asarray(X), y


def _get_pos_ftr(idx, doc_lst):
    """
    mapping of pos tagging to integer

    @param integer: the index of the token to get the pos tag code
    @param [(string,string)]: a list of tuples of the format (token, pos_tag)

    @return integer: a integer code that represents a pos tag
    """

    if idx < 0 or idx >= len(doc_lst):
        return pos2idx["<S>"]
    else:
        if len(doc_lst[idx]) > 2:
            (tok, pos, ann) = doc_lst[idx]
        else:
            (tok, pos) = doc_lst[idx]

        return pos2idx[pos]  # pos tag


def _extract_features_train(doc):
    """
    build features for each sentence tokenized by spacy

    @param document: a sentence as document type (spacy)

    @return np.array: an array of pos tagging features of a given text
    """
    ftrs = []
    idx = 0
    window = WINDOW_SIZE

    tok_lst = [(tok.text, tok.pos, tok.ann) for tok in doc]

    for (tok, pos, ann) in tok_lst:
        tok_ftrs = []

        for i in range(idx - window, idx + window + 1):
            tok_ftrs.append(_get_pos_ftr(i, tok_lst))

        if ann == 'Event':
            tok_ftrs.append("I")
        else:
            tok_ftrs.append("O")

        idx += 1
        ftrs.append(tok_ftrs)

    return np.array(ftrs)


def _extract_features(doc):
    """
    build features for each sentence tokenized by spacy

    @param document: a sentence as document type (spacy)

    @return np.array: an array of pos tagging features of a given text
    """
    ftrs = []
    idx = 0
    window = WINDOW_SIZE

    tok_lst = [(tok.text, tok.pos_) for tok in doc]

    for (tok, pos) in tok_lst:
        tok_ftrs = []

        for i in range(idx - window, idx + window + 1):
            tok_ftrs.append(_get_pos_ftr(i, tok_lst))

        idx += 1
        ftrs.append(tok_ftrs)

    return np.array(ftrs)


def execute_train(data_dir, reader, output_model="gb_custom_event_pt.joblib"):
    """
    Method to train a model to classify events, given a dataset

    @param string: path to the train data
    @param ReadBrat: a reader of the corpus
    @param string: the name of the podel to persist

    @return None
    """

    data_tokens = reader.process(data_dir)
    all_ftrs = []

    for doc in data_tokens:
        doc_ftrs = _extract_features_train(doc)
        all_ftrs.append(doc_ftrs)
    clf = GradientBoostingClassifier(random_state=0)

    idx_lst = list(range(len(data_tokens)))
    X_train, y_train = _get_data(idx_lst, all_ftrs)

    # cc = SMOTE(random_state=0) # oversampling technique
    # X_resampled, y_resampled = cc.fit_resample(X_train, y_train)

    # clf.fit(X_resampled, y_resampled)
    clf.fit(X_train, y_train)

    joblib.dump(clf, output_model)


def _get_verb_pos(verb, tok_lst, idx_start):
    """
    It get the verb index in a given token list. The first occurrence,
    starting from idx_start index position

    @param string: the verb
    @param [string]: a list of tokens
    @param int: the starting point to start the search for the verb

    @return int: the verb index in the token list
    """

    idx = idx_start
    while idx < len(tok_lst):
        if tok_lst[idx] == verb:
            break
        idx = idx + 1

    return idx


def _set_role_token(tokcorpus_lst, idx_verb, args):
    """
    It sets the role position for each token in the tokcorpus_lst list

    @param [TokenCorpus]: a list of TokenCorpus objects
    @param int: the index of the current governing verb of the given argument
              structure
    @param dict: The dictionary that stores the argument structure of an SRL
                labeling returned by the nlpnet API

    @return [TokenCorpus]: the list of TokenCorpus objects updated with
                governing verb and srl role
    """

    # TODO 1: It is possible implement a more efficient method?
    # TODO 2: Perform a more complete test to see what examples does not work
    # here

    for role in args:
        for tok in args[role]:
            # talvez começar analise APOS idx_verb e, tokcorpus_lst!
            # nao pode, pois tem argumentos antes de idx_verb
            # Verbo mais proximo? Como saber qual eh o mais proximo?
            #  guardar posicao do gov_verb
            for idx_corpus, tokcorpus in enumerate(tokcorpus_lst):
                if tok == tokcorpus.text:

                    # if still there is no role
                    if tokcorpus.srl is None:
                        tokcorpus.gov_verb = tokcorpus_lst[idx_verb].text
                        tokcorpus.gov_verb_idx = idx_verb
                        tokcorpus.srl = role
                        break
                    else:
                        # if there is role, but there is a more specific governing verb
                        # then assign a new role and a new governing verb
                        if tokcorpus.gov_verb_idx is not None:
                            # the nearest verb is more probable to be the gpverning verb
                            # so, this kind a heuristic according to the
                            # nlpnet output
                            dist_verb = abs(idx_corpus - idx_verb)
                            dist_gov_verb = abs(idx_corpus - tokcorpus.gov_verb_idx)
                            if tokcorpus.gov_verb != tokcorpus_lst[idx_verb].text and \
                                    dist_verb <= dist_gov_verb:
                                tokcorpus.gov_verb = tokcorpus_lst[idx_verb].text
                                tokcorpus.srl = role

    # for tokcorpus in tokcorpus_lst:
    #    print(tokcorpus.text, tokcorpus.srl, tokcorpus.gov_verb)
    return tokcorpus_lst


def _get_srl_tags(sent):
    """
    Given a sentence, it labels using a srl tagger

    @param Sentence object (spacy)
    @return [Toke]
    """

    tok_lst = [tok.text for tok in sent]
    tags = pipeline["srl_tagger"].tag_tokens(tok_lst)

    all_toks_lst = []

    # tracking position of the verbs in the argument
    # structures
    last_verb_idx = 0
    new_arg_lst = []
    for (verb, args) in tags.arg_structures:
        idx_verb = _get_verb_pos(verb, tags.tokens, last_verb_idx)
        last_verb_idx = idx_verb
        new_arg_lst.append((verb, args, idx_verb))

    # mapping roles to tokens, using the governing verb positio
    tokcorpus_lst = [TokenCorpus(tok) for tok in tags.tokens]
    for verb, args, idx_verb in new_arg_lst:
        tokcorpus_lst = _set_role_token(tokcorpus_lst, idx_verb, args)
    all_toks_lst = all_toks_lst + tokcorpus_lst

    return all_toks_lst


def doc2featureCRF(doc):
    data_doc = []
    y_doc = []

    srl_toks = []
    for sent in doc.sents:
        srl_toks += _get_srl_tags(sent)

    idx = 0
    for sent in doc.sents:
        sent_doc = []
        for tok in sent:

            data_ = {}

            data_["token"] = tok.text
            data_["lemma"] = tok.lemma_
            data_["head"] = tok.head.text
            data_["head_lemma"] = tok.head.lemma_
            # data_["gov_verb"] = tok.gov_verb

            data_["head_pos"] = tok.head.pos_
            data_["pos"] = tok.pos_

            if srl_toks[idx].gov_verb is None:
                data_["gov_verb"] = "NULL"
            else:
                data_["gov_verb"] = srl_toks[idx].gov_verb

            if srl_toks[idx].srl is None:
                data_["role"] = "NULL"
            else:
                data_["role"] = srl_toks[idx].srl

            sent_doc.append(data_)

        data_doc.append(sent_doc)

    return data_doc


def extract_events(lang, text):
    """
    Main function that applies the custom tagger to extract event entities from each sentence.

    @param lang: The language of the text
    @param text: The full text to be annotated

    @return: Pandas DataFrame with every event entity and their character span
    """
    # 1. use spacy to tokenize and to get pos tags
    doc = pipeline["pos_tagger"]((text))

    # FIND EVENTS#
    # ftrs = _extract_features(doc)
    # TODO: o que esta acontecendo que no teste unitario temos mais
    # que três frases..Esta estranho
    ftrs = doc2featureCRF(doc)

    clf = pipeline["event_tagger"]
    y = clf.predict(ftrs)

    result = {"actor": [], "char_span": []}

    # colocar em outro formato aqui
    idx_sent = 0
    for sent in doc.sents:
        idx_tok = 0
        for tok in sent:
            if y[idx_sent][idx_tok] == "I-EVENT" or y[idx_sent][idx_tok] == "B-EVENT":
                result["actor"].append(tok.text)
                result["char_span"].append((tok.idx, tok.idx + len(tok.text)))
            idx_tok += 1
        idx_sent += 1

    return pd.DataFrame(result)


if __name__ == "__main__":
    load()
    # data_dir = "data/train"
    # reader = ReadBrat()
    # execute_train(data_dir, reader)
    # unit test
    # ans = extract_events("pt","O cavalo correu na pista de corrida. E tudo deu certo naquele dia. Depois o cavalo assaltou um casal.")
    # print(ans)

