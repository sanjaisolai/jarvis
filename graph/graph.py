from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from llm.jarvis import call_llm
from tools.tools import web_search_tool,communication_subagent_tool, list_calendar_events, create_calendar_event,delete_calendar_event, search_memories_tool, system_subagent_tool, ui_subagent_tool
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    messages: Annotated[list, add_messages]


def should_tool_call(state: State):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return 'tools'
    return END


tool_node = ToolNode([web_search_tool,communication_subagent_tool, list_calendar_events, create_calendar_event,delete_calendar_event, search_memories_tool, system_subagent_tool, ui_subagent_tool ])
    
workflow = StateGraph(State)
workflow.add_node('jarvis', call_llm)
workflow.add_node('tool_node', tool_node)
workflow.add_edge(START, 'jarvis')
workflow.add_conditional_edges(
    'jarvis',
    should_tool_call,
    {
        'tools': 'tool_node',
        END: END,
    },
)
workflow.add_edge('tool_node', 'jarvis')

checkpointer = InMemorySaver()

graph = workflow.compile(
    checkpointer=checkpointer
)