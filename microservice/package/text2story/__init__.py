import sys
from pathlib import Path

from text2story.annotators import load
from text2story.annotators import get_available_tools
from text2story.annotators import get_participant_tools
from text2story.annotators import get_event_tools
from text2story.annotators import get_time_tools


def start():
    print("Loading models......")
    load()
    print("Loading models...... OK!")

def get_tools_name():
    return get_available_tools()

def participant_tool_names():
    return get_participant_tools()

def event_tool_names():
    return get_event_tools()

def time_tool_names():
    return get_time_tools()


# Export to out of the package
from text2story.core.narrative import Narrative
