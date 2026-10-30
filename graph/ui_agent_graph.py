from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from llm.ui_agent import call_ui_llm
from tools.ui_tools import (
    create_ui,
    update_ui,
    remove_ui,
    clear_ui
)



class State(TypedDict):
    messages: Annotated[list, add_messages]

def should_tool_call(state: State):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return 'tools'
    return END


tool_node = ToolNode([
    create_ui,
    update_ui,
    remove_ui,
    clear_ui
])


workflow = StateGraph(State)

workflow.add_node('ui_agent', call_ui_llm)
workflow.add_node('tool_node', tool_node)
workflow.add_edge(START, 'ui_agent')
workflow.add_conditional_edges(
    'ui_agent',
    should_tool_call,
    {
        'tools':'tool_node',
        END:END
    }
)

workflow.add_edge('tool_node',END)

ui_graph = workflow.compile()