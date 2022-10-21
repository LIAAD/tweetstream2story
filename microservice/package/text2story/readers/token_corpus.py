class TokenCorpus:
    """
    This class should store the token text, and
    annotation information
    """

    def __init__(self, text=None, token_id=None, sentence=None):
        # fields in the Token object
        self.text = text
        self.id = token_id
        self.lemma = None
        self.ann = None
        self.sentence = sentence
        self.pos = None
        self.dep = None
        self.head = None
        self.head_pos = None
        self.head_lemma = None
        self.gov_verb = None
        self.gov_verb_idx = None
        self.srl = None

        self.offset = None
