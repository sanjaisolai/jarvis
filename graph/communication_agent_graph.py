from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from tools.communication_tools import search_emails, send_email, list_calendar_events, create_calendar_event, get_thread, reply_to_email, search_memories_tool
from langgraph.checkpoint.memory import InMemorySaver
from llm.communication_agent import call_llm

class State(TypedDict):
    messages: Annotated[list, add_messages]

def should_tool_call(state: State):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return 'tools'
    return END


tool_node = ToolNode([search_emails, send_email, list_calendar_events, create_calendar_event, get_thread, reply_to_email, search_memories_tool])


workflow = StateGraph(State)

workflow.add_node('communication_llm', call_llm)
workflow.add_node('tool_node', tool_node)
workflow.add_edge(START, 'communication_llm')
workflow.add_conditional_edges(
    'communication_llm',
    should_tool_call,
    {
        'tools': 'tool_node',
        END: END,
    },
)

workflow.add_edge('tool_node', 'communication_llm')

checkpointer = InMemorySaver()

communication_graph = workflow.compile(
    checkpointer=checkpointer
)