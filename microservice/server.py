import os
import pickle
import socket
import sys
from threading import Thread, Event
import traceback

sys.path.insert(1, os.path.join(sys.path[0], 'package'))
sys.path.insert(2, os.path.join(sys.path[0], 'package/text2story'))
sys.path.insert(3, os.path.join(sys.path[0], 'brat2viz/brat2drs'))
sys.path.insert(3, os.path.join(sys.path[0], 'brat2viz/drs2viz'))

import package.text2story as t2s
from package.text2story.core.narrative import Narrative
from brat2viz.brat2drs.brat2drs import read_file, main
from brat2viz.drs2viz import parser


def startup():
    t2s.start()

    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    data_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    data_sock.bind(('', 65432))

    data_sock.listen()

    print("Listening for users")

    return data_sock


class Producer(Thread):

    def __init__(self, queue, event, data_sock):
        Thread.__init__(self)
        self.queue = queue
        self.event = event
        self.data_sock = data_sock

    def run(self):
        while True:
            try:
                self.queue.append(self.data_sock.accept())
                self.event.set()
                self.event.clear()

            except Exception as e:
                print(e)

        data_sock.close()


class Consumer(Thread):

    def __init__(self, queue, event):
        Thread.__init__(self)
        self.queue = queue
        self.event = event

    def run(self):

        while True:
            self.event.wait(1)

            if len(self.queue) == 0:
                continue

            conn, _ = self.queue.pop(0)
            starting_path = os.getcwd()

            try:
                msg_received = pickle.loads(conn.recv(75000000))
            except Exception as e:
                print(e)
                conn.sendall(pickle.dumps({"error": "Text too large"}))
                conn.close()
                continue
    
            try:
                print(f"Message received on server side: \n{msg_received}")

                tools_normalized_actors = []
                tools_normalized_time = []
                tools_normalized_events = []
                tools_normalize_objectal_links = []
                tools_semantic_role_labeling = []
                OBJECTAL_LINKS_RESOLUTION_TOOLS = ['spacy']
                SEMANTIC_ROLE_LABELLING_TOOLS = ['allennlp']

                for tool in msg_received['tools'].keys():
                    if msg_received['tools'][tool] is False:
                        continue
                    if tool == 'AllenNLP':
                        tools_normalized_events.append('allennlp')
                    elif tool == 'NLTK' and msg_received['lang'] == 'en':
                        tools_normalized_actors.append('nltk')
                    elif tool == 'Spark NLP':
                        # tools_normalized_actors.append('sparknlp')
                        pass
                    elif tool == 'py_heideltime':
                        tools_normalized_time.append('py_heideltime')
                    elif tool == 'spaCy':
                        tools_normalized_actors.append('spacy')
                    elif tool == 'Spacy (Objectal Linking)' and msg_received['lang'] == 'en':
                        tools_normalize_objectal_links.append('spacy')
                    elif tool == 'AllenNLP (Sematic Role Labeling)':
                        tools_semantic_role_labeling.append('allennlp')

                print("Creating narrative...")
                narrative = Narrative(msg_received['lang'], msg_received['text'], msg_received['publication_date'])
                if len(tools_normalized_actors):
                    narrative.extract_actors(*tools_normalized_actors)

                if len(tools_normalized_time):
                    narrative.extract_times(*tools_normalized_time)

                if len(tools_normalized_events):
                    narrative.extract_events(*tools_normalized_events)

                if len(tools_normalize_objectal_links):
                    narrative.extract_objectal_links(*tools_normalize_objectal_links)

                if len(tools_semantic_role_labeling):
                    narrative.extract_semantic_role_links(*tools_semantic_role_labeling)

                print("Generating annotation...")
                ann_raw_str = narrative.ISO_annotation()

                with open(os.path.join(os.getcwd(), 'brat2viz', 'brat2drs', 'text_2_viz_temp', 'text.txt'), 'w+') as f:
                    f.writelines(msg_received['text'])

                with open(os.path.join(os.getcwd(), 'brat2viz', 'brat2drs', 'text_2_viz_temp', 'text.ann'), 'w+') as f:
                    f.writelines(ann_raw_str)


                os.chdir(os.path.join(os.getcwd(), 'brat2viz', 'brat2drs'))

                ann_raw_str = main('text_2_viz_temp')

                os.chdir(os.path.join(starting_path, 'brat2viz', 'drs2viz'))

                drs_file = os.path.join('..', 'drs_files', 'text_drs.txt')

                actors_dict, events_dict, events_relations, non_event_relations = parser.parse_drs(drs_file)

                msc_string = parser.get_msc_data(drs_file)

                actors_dict, non_event_relations, event_relations = parser.get_graph_data(drs_file)

                drs_raw_str = parser.get_drs_str(drs_file)

                conn.sendall(pickle.dumps({
                    'input_text': msg_received['text'],
                    'ann_str': ann_raw_str,
                    'drs_str': drs_raw_str,
                    'msc_string': msc_string,
                    'actors_dict': actors_dict,
                    'events_dict': events_dict,
                    'event_relations': event_relations,
                    'non_event_relations': non_event_relations,
                }))

            except Exception as e:
                traceback.print_exc()
                conn.sendall(pickle.dumps({"error": e}))

            finally:
                os.chdir(starting_path)
                conn.close()


if __name__ == '__main__':
    event = Event()

    queue = []

    data_sock = startup()

    consumer, producer = (Consumer(queue, event), Producer(queue, event, data_sock))

    producer.start()
    consumer.start()

    producer.join()
    consumer.join()
