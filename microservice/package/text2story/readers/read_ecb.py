import os
import sys
import xml.etree.ElementTree as ET

from read import Read
from token_corpus import TokenCorpus

from package.text2story.core.narrative import Narrative
from package.text2story.core.entity_structures import ActorEntity, EventEntity, TimeEntity
from package.text2story.readers.read_brat import ReadBrat


class ReadECB(Read):
    def __init__(self) -> None:
        self.root = None
        self.tokens = []
        self.actors = []
        self.events = []
        self.times = []
        self.narrative = Narrative("en", "", "2021-08-08")
        self.read_brat = ReadBrat()

    def process(self, data_dir):
        return self.read_brat.process(data_dir)

    def process_file(self, data_file):
        return self.read_brat.process_file(data_file)

    def convert_xml_to_brat(self, xml_path, data_dir, output_path):
        files_list = []

        for dir_path, dirs, files in os.walk(xml_path):
            for f in files:
                files_list.append({
                    'file': f.replace('.xml', ''),
                    'path': dir_path
                })

        for index, file_dict in enumerate(files_list):
            print(f'Processing file {file_dict["file"]} No: {index + 1} out of {len(files_list)}')
            self.generate_ann_txt_file(file_dict['path'], file_dict['file'], data_dir)

    def generate_ann_txt_file(self, file_path, file_name, data_dir):
        tree = ET.parse(f'{file_path}/{file_name}.xml')
        self.root = tree.getroot()

        txt_file = open(f'{data_dir}/{file_name}.txt', 'w')
        ann_file = open(f'{data_dir}/{file_name}.ann', 'w')

        self.erase_data_structures()

        self.reconstruct_narrative(txt_file)
        self.findall_actors()
        self.findall_events()
        self.findall_time()

        self.fill_narrative()
        self.construct_ann(self.narrative.ISO_annotation(), ann_file)

    def reconstruct_narrative(self, txt_file):
        for token in self.root.iter('token'):
            self.tokens.append(TokenCorpus(token.text.strip(), token.attrib['t_id'], token.attrib['sentence']))

        current_sentence = 0
        char_counter = 0
        string_to_file = ""

        for token in self.tokens:

            if int(token.sentence) > current_sentence:
                current_sentence = current_sentence + 1
                string_to_file += "\n"

            if token.text != ";" and token.text != "," and token.text != "'" and token.text != ".":
                string_to_file += ' '
                char_counter += 1

            string_to_file += token.text
            # TODO: I dont understand why we need +1 but we need it
            token.offset = char_counter + 1
            char_counter += len(token.text)

        txt_file.write(string_to_file)
        txt_file.flush()
        txt_file.close()

    def findall_actors(self):
        self.findall_human_actors()
        self.findall_org_actors()
        self.findall_loc_actors()
        self.findall_obj_actors()
        self.findall_other_actors()

    def findall_human_actors(self):
        for actor in self.root.iter('HUMAN_PART_PER'):

            actor_token_index_list = []

            for anchor in actor.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                actor_token_index_list.append(int(t_id))

            if len(actor_token_index_list) > 0:
                self.actors.append(self.process_actor_token_list(actor_token_index_list, "Noun", "Per"))

    def findall_org_actors(self):
        for actor in self.root.iter('HUMAN_PART_ORG'):

            actor_token_index_list = []

            for anchor in actor.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                actor_token_index_list.append(int(t_id))

            if len(actor_token_index_list) > 0:
                self.actors.append(self.process_actor_token_list(actor_token_index_list, "Noun", "Org"))

    def findall_loc_actors(self):
        for actor in self.root.iter('HUMAN_PART_GPE'):

            actor_token_index_list = []

            for anchor in actor.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                actor_token_index_list.append(int(t_id))

            if len(actor_token_index_list) > 0:
                self.actors.append(self.process_actor_token_list(actor_token_index_list, "Noun", "Loc"))

    def findall_obj_actors(self):
        for actor in self.root.iter('HUMAN_PART_VEH'):

            actor_token_index_list = []

            for anchor in actor.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                actor_token_index_list.append(int(t_id))

            if len(actor_token_index_list) > 0:
                self.actors.append(self.process_actor_token_list(actor_token_index_list, "Noun", "Obj"))

        for actor in self.root.iter('NON_HUMAN_PART'):

            actor_token_index_list = []

            for anchor in actor.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                actor_token_index_list.append(int(t_id))

            if len(actor_token_index_list) > 0:
                self.actors.append(self.process_actor_token_list(actor_token_index_list, "Noun", "Obj"))

        for actor in self.root.iter('NON_HUMAN_PART_GENERIC'):

            actor_token_index_list = []

            for anchor in actor.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                actor_token_index_list.append(int(t_id))

            if len(actor_token_index_list) > 0:
                self.actors.append(self.process_actor_token_list(actor_token_index_list, "Noun", "Obj"))

    def findall_other_actors(self):
        for actor in self.root.iter('HUMAN_PART_FAC'):

            actor_token_index_list = []

            for anchor in actor.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                actor_token_index_list.append(int(t_id))

            if len(actor_token_index_list) > 0:
                self.actors.append(self.process_actor_token_list(actor_token_index_list, "Noun", "Other"))

        for actor in self.root.iter('HUMAN_PART_MET'):

            actor_token_index_list = []

            for anchor in actor.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                actor_token_index_list.append(int(t_id))

            if len(actor_token_index_list) > 0:
                self.actors.append(self.process_actor_token_list(actor_token_index_list, "Noun", "Other"))

    def process_actor_token_list(self, index_list, lexical_head, actor_type):
        raw_str = ""

        for index in index_list:
            raw_str += self.tokens[index - 1].text + " "

        raw_str = raw_str.rstrip()

        return ActorEntity(raw_str, (
            self.tokens[index_list[0] - 1].offset, self.tokens[index_list[0] - 1].offset + len(raw_str)),
                           lexical_head,
                           actor_type)

    def findall_events(self):
        self.findall_action_occurrence()
        self.findall_action_perception()
        self.findall_action_reporting()
        self.findall_action_aspectual()
        self.findall_action_state()
        self.findall_action_causative()
        self.findall_action_generic()

    def findall_action_occurrence(self):
        for event in self.root.iter('ACTION_OCCURRENCE'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Occurrence", "Pos"))

        for event in self.root.iter('NON_ACTION_OCCURRENCE'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Occurrence", "Neg"))

    def findall_action_perception(self):
        for event in self.root.iter('ACTION_PERCEPTION'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Perception", "Pos"))

        for event in self.root.iter('NON_ACTION_PERCEPTION'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Perception", "Neg"))

    def findall_action_reporting(self):
        for event in self.root.iter('ACTION_REPORTING'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Reporting", "Pos"))

        for event in self.root.iter('NON_ACTION_REPORTING'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Reporting", "Neg"))

    def findall_action_aspectual(self):
        for event in self.root.iter('ACTION_ASPECTUAL'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Aspectual", "Pos"))

        for event in self.root.iter('NON_ACTION_ASPECTUAL'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Aspectual", "Neg"))

    def findall_action_state(self):
        for event in self.root.iter('ACTION_STATE'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "State", "Pos"))

        for event in self.root.iter('NON_ACTION_STATE'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "State", "Neg"))

    def findall_action_causative(self):
        for event in self.root.iter('ACTION_CAUSATIVE'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Causative", "Pos"))

        for event in self.root.iter('NON_ACTION_CAUSATIVE'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Causative", "Neg"))

    def findall_action_generic(self):
        for event in self.root.iter('ACTION_GENERIC'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Generic", "Pos"))

        for event in self.root.iter('NON_ACTION_GENERIC'):

            event_token_index_list = []

            for anchor in event.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                event_token_index_list.append(int(t_id))

            if len(event_token_index_list) > 0:
                self.events.append(self.process_event_token_list(event_token_index_list, "Generic", "Neg"))

    def process_event_token_list(self, index_list, event_class, polarity):
        raw_str = ""

        for index in index_list:
            raw_str += self.tokens[index - 1].text + " "

        raw_str = raw_str.rstrip()

        return EventEntity(raw_str,
                           (self.tokens[index_list[0] - 1].offset,
                            self.tokens[index_list[0] - 1].offset + len(raw_str)),
                           event_class, polarity)

    def findall_time(self):
        self.findall_time_date()
        self.findall_time_of_day()
        self.findall_time_duration()
        self.findall_time_repetition()

    def findall_time_date(self):
        for time in self.root.iter('TIME_DATE'):

            time_token_index_list = []

            for anchor in time.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                time_token_index_list.append(int(t_id))

            if len(time_token_index_list) > 0:
                self.times.append(self.process_time_token_list(time_token_index_list, "Date", "Date"))

    def findall_time_of_day(self):
        for time in self.root.iter('TIME_OF_THE_DAY'):

            time_token_index_list = []

            for anchor in time.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                time_token_index_list.append(int(t_id))

            if len(time_token_index_list) > 0:
                self.times.append(self.process_time_token_list(time_token_index_list, "Time", "Time"))

    def findall_time_duration(self):
        for time in self.root.iter('TIME_DURATION'):

            time_token_index_list = []

            for anchor in time.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                time_token_index_list.append(int(t_id))

            if len(time_token_index_list) > 0:
                self.times.append(self.process_time_token_list(time_token_index_list, "Duration", "Duration"))

    def findall_time_repetition(self):
        for time in self.root.iter('TIME_REPETITION'):

            time_token_index_list = []

            for anchor in time.findall('token_anchor'):
                t_id = anchor.attrib['t_id']
                time_token_index_list.append(int(t_id))

            if len(time_token_index_list) > 0:
                self.times.append(self.process_time_token_list(time_token_index_list, "Time", "Set"))

    def process_time_token_list(self, index_list, value, timex_type):
        raw_str = ""

        for index in index_list:
            raw_str += self.tokens[index - 1].text + " "

        raw_str = raw_str.rstrip()

        return TimeEntity(raw_str, (
            self.tokens[index_list[0] - 1].offset, self.tokens[index_list[0] - 1].offset + len(raw_str)), value,
                          timex_type)

    def fill_narrative(self):
        actors_dict = {}
        events_dict = {}
        times_dict = {}

        for index, actor in enumerate(self.actors):
            actors_dict['T' + str(index)] = actor

        for index, event in enumerate(self.events):
            events_dict['E' + str(index)] = event

        for index, time in enumerate(self.times):
            times_dict['T' + str(index)] = time

        self.narrative.actors = actors_dict
        self.narrative.events = events_dict
        self.narrative.times = times_dict

    def construct_ann(self, iso_annotation, ann_file):
        ann_file.write(iso_annotation)
        ann_file.flush()
        ann_file.close()

    def to_column(self, data_dir, output_dir):
        return self.read_brat.toColumn(data_dir, output_dir)

    def erase_data_structures(self):
        self.tokens = []
        self.actors = []
        self.events = []
        self.times = []
        self.narrative = Narrative("en", "", "2021-08-08")


def main(xml_dir: str = None, data_dir: str = None, output_dir: str = None):
    if not xml_dir:
        if "XML_DIR" in os.environ.keys():
            xml_dir = xml_dir = os.environ.get("XML_DIR")
        else:
            print("Invalid XML_DIR")
            return

    if not data_dir:
        if "DATA_DIR" in os.environ.keys():
            data_dir = data_dir = os.environ.get("DATA_DIR")
        else:
            print("Invalid DATA_DIR")
            return

    if not output_dir:
        if "OUTPUT_DIR" in os.environ.keys():
            output_dir = output_dir = os.environ.get("OUTPUT_DIR")
        else:
            print("Invalid OUTPUT_DIR")
            return

    r = ReadECB()
    r.convert_xml_to_brat(xml_dir, data_dir, output_dir)
    r.to_column(data_dir, output_dir)


if __name__ == '__main__':
    main(f'/home/ruben/Desktop/FEUP/text2story/projeto/Data/ecb+/in',
         f'/home/ruben/Desktop/FEUP/text2story/projeto/Data/ecb+/mid',
         f'/home/ruben/Desktop/FEUP/text2story/projeto/Data/ecb+/results')
