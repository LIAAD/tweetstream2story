from text2story.annotators.CUSTOMPT.srl_bert_pt import my_model,my_reader
from allennlp_models.structured_prediction.predictors import SemanticRoleLabelerPredictor
from allennlp.predictors.predictor import Predictor
from allennlp.models import Model
from overrides import overrides
from allennlp.models.archival import load_archive
from typing import List, Iterator, Optional
from nltk import tokenize, download
download('punkt')

from allennlp.data import DatasetReader, Instance
from allennlp.common.util import JsonDict

@Predictor.register("my_predictor")
class predict(SemanticRoleLabelerPredictor):
    def __init__(
        self, model: Model, dataset_reader: DatasetReader
    ) -> None:
        super().__init__(model, dataset_reader, "pt_core_news_lg")

    @overrides
    def load_line(self, line: str) -> Iterator[str]:
        for sentence in tokenize.sent_tokenize(line):
            yield sentence

    @overrides
    def dump_line(self, outputs) -> str:
        output_file=open("output.txt", "a",encoding="utf-8")
        return json.dump(outputs, output_file,ensure_ascii=False)



    @overrides
    def _sentence_to_srl_instances(self, sentence):
        new_sent=""
        for char in sentence:
            new_sent+=char if char!="-" else " -"
        tokens = self._tokenizer.tokenize(new_sent)
        return self.tokens_to_instances(tokens)

    @overrides
    def predict_json(self, inputs: str):
        instances = self._sentence_to_srl_instances(inputs)
        if not instances:
            return inputs.split()
        return self.predict_instances(instances)

    @overrides
    def predict_instances(self, instances: List[Instance]) -> JsonDict:
        outputs = self._model.forward_on_instances(instances)
        results = {"verbs": [], "words": outputs[0]["words"]}
        for output in outputs:
            tags = output["tags"]
            description = self.make_srl_string(output["words"], tags)
            results["verbs"].append(
                {"verb": output["verb"], "description": description, "tags": tags}
            )
        return results

class TagSRL():

    def __init__(self, model_path):

        archive = load_archive(model_path)

        self.predictor = Predictor.from_archive(
            archive, "my_predictor", dataset_reader_to_load="train"
        )

    def tag(self, text):

        return  self.predictor.predict_json(text)

