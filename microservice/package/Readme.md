# Text2Story main package
The Text2Story main package contains the main classes and methods for the T2S pipeline: from text to formal representation to visualization or other representation.

- **Relation to Brat2Viz**
The Text2Story package is a generalization of Brat2Viz and should in fact contain all the funcionalities and variants of the T2S project output.


## Structure
```
.
│   README.md
|   env.yml
│   requirements.txt
|
└──Text2Story
      └──core
      │   │   annotator.py (META-annotator)
      │   │   entity_structures.py (ActorEntity, TimexEntity and EventEntity classes)
      │   |   exceptions.py (Exceptions raised by the package)
      │   |   link_structures.py (TemporalLink, AspectualLink, SubordinationLink, SemanticRoleLink and ObjectalLink classes)
      │   |   narrative.py (Narrative class)
      │   |   utils.py (Utility functions)
      │   
      └───annotators (tools supported by the package to do the extractions)
      |   |   NLTK
      |   │   PY_HEIDELTIME
      |   |   SPACY
      |   |   SPARKNLP
|
└── Webapp
      |  backend.py
      |  main.py
      |  session_state.py
      |  input_phase.py
      |  output_phase.py

```

## Classes
### Entity classes
- **ActorEntity** 🟢
    - attributes
        - text : str
        - character_span : (int, int)
        - value : str
        - type : str
        - individuation : str (HARDCODED)
        - involvement : str  (HARDCODED)

- **TimexEntity** 🟢
    - attributes
        - text : str
        - character_span : (int, int)
        - value : str
        - type : str
        - temporal_function : boolean (HARDCODED)
        - anchor_time : str (HARDCODED)

- **EventEntity** 🟢
    - attributes
        - text : str
        - character_span : str
        - event_class : str (HARDCODED)
        - polarity : str (HARDCODED)
        - factuality : str (HARDCODED)
        - tense : str (HARDCODED)

### Link classes

- **TemporalLink** 🔴

- **AspectualLink** 🔴

- **SubordinationLink** 🔴

- **SemanticRoleLink** 🟢
    - attributes
        - type : str
        - actor : str
        - event : str

- **ObjectalLink** 🟢
    - attributes
        - type : str  (HARDCODED)
        - arg1 : str
        - arg2 : str

### Other classes
- **Narrative**
    - attributes
        - lang : str 🟢
        - text : str 🟢
        - publication_time : str 🟢
        - actors : {str -> ActorEntity} 🟢
        - timex : {str -> TimexEntity} 🟢
        - events : {str -> EventEntity} 🟢
        - tlinks : 🔴
        - ref_rels : 🔴
        - obj_links : {str -> SemanticRoleLink} 🟢
        - sem_links : {str -> ObjectalLink} 🟢
    - methods
        - extract_actors: given a list of tools to do the extraction with, updates self.actors and returns it 🟢
        - extract_times: given a list of tools to do the extraction with, updates self.timexs and returns it 🟢
        - extract_events: given a list of tools to do the extraction with, updates self.events and returns it 🟢
        - extract_semantic_role_links: given a list of tools to do the extraction with, finds semantic role links between extracted actors (self.actors) and events (self.events), updates self.sem_links and returns it. 🟢
        - extract_objectal_links: given a list of tools to do the extraction with, updates self.obj_links and returns it 🟢
        - tempsort_events: given two or more events (spans?), outputs the temporal relationship between them. Output ISO dictionary. 🔴
        - ISO_annotation: returns ISO annotation in .ann format 🟢
        - import_ISO_annotation: imports ISO annotation from file (may not be trivial, because of the organization by type) 🔴
        - drs: outputs list with drs formulae (txt) 🔴
        - compare_annotations: compare ISO annotation given with the one here (should annotation be an attribute) 🔴

- **drs** 🔴
    - attributes
        - drs: list with text or structure with formulae
    - methods
        - msc: plot msc
        - kowledge_graph: plot knowledge_graph
        - icons: plot icon strip
        - pretty_print:

### Annotators
All annotators have the same interface: they implement a function called 'extract_' followed by the name of the particular extraction.
E.g., if they are extracting actors, then they implement a function named 'extract_actors', with two arguments: the language of text and the text itself.

|  Extractions |           Interface                                      |     Supporting tools  |
|      ---     |             ---                                          |           ---         |
|     Actor    | extract_actors(lang, text)                               | SPACY, SPARKNLP, NLTK |
|    Timexs    | extract_timexs(lang, text, publication_time)             |      PY_HEIDELTIME    |
| ObjectalLink | extract_objectal_links(lang, text, publication_time)     |        ALLENNLP       |
|     Event    | extract_events(lang, text, publication_time)             |        ALLENNLP       |
| SemanticLink | extract_semantic_role_link(lang, text, publication_time) |        ALLENNLP       |

To **change some model used in the supported tools**, just go to text2story/annotators/ANNOTATOR_TO_BE_CHANGED and change the model in the file: \_\_init\_\_.py.

To **add a new tool**, add a folder to text2story/annotators with the name of the annotator all capitalized (just a convention; useful to avoid name colisions).
In that folder, create a file called '\_\_init\_\_.py' and there implement a function load() and the desired extraction functions.
The function load() should load the pipeline to some variable defined by you, so that, every time we do an extraction, we don't need to load the pipeline all over again. (Implement it, even if your annotator doesn't load anything. Leave it with an empty body.)

In the text2story.annotators.\_\_init\_\_.py file, add a call to the load() function, and to the extract functions.
(See the already implemented tools for guidance.)

And it should be done.

PS: Don't forget to normalize the labels to our semantic framework!

### Usage
#### Terminal
```python
import text2story as t2s # Import the package

t2s.start() # Load the pipelines

text = 'On Friday morning, Max Healthcare, which runs 10 private hospitals around Delhi, put out an "SOS" message, saying it had less than an hour\'s supply remaining at two of its sites. The shortage was later resolved.'

doc = t2s.Narrative('en', text, '2020-05-30')

doc.extract_actors() # Extraction done with all tools.
doc.extract_actors('spacy', 'nltk') # Extraction done with the SPACY and NLTK tools.
doc.extract_actors('sparknlp') # Extraction done with just the SPARKNLP tool.

doc.extract_timexs() # Extraction done with all tools (same as specifying 'py_heideltime', since we have just one tool to extract timexs)

doc.extract_objectal_links() # Extraction of objectal links from the text with all tools (needs to be done after extracting actors, since it requires actors to make the co-reference resolution)

doc.extract_events() # Extraction of events with all tools
doc.extract_semantic_role_link() # Extraction of semantic role links with all tools (should be done after extracting events since most semantic relations are between an actor and an event)

doc.ISO_annotation('annotations.ann') # Outputs ISO annotation in .ann format (txt) in a file called 'annotations.ann'
```
#### Web app
```ssh
python backend.py
streamlit run main.py
```
and a page on your browser will open!

### Known bugs
- (T2S) Generated ID's keep counting when we reextract actors/timexs.
- (Web app) No possibility to create a narrative without a publication time.
- (Web app) Bug in the frontend: a option from the sidebar of the input phase appears on the output phase

### Functionalities to be incorporated

- From text / general (Pedro Mota)
    - Generate an ISO annotation from raw text
    - Enable different alternatives for obtaining different narrative elements
    - Import an ISO annotation
    - Extend an existing ISO annotation
    - Generate DRS from ISO annotation (adapt from Brat2Viz)
- From DRS
    - Visualize DRS as MSC (adapt from Brat2Viz - Pedro Mota)
    - Visualizae DRS as Knowledge Graphs (adapt from Brat2Viz - Pedro Mota)
    - Visualize DRS as Icon strips (Joana Valente)
    - Visualize DRS as Storylines (Mariana)
- From tweets (Vasco Campos)
    - Generate an ISO annotation from one tweet
    - Generate an ISO annotation from a set of tweets
