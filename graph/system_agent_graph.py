from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from llm.system_agent import call_system_llm

from tools.system_tools import (
    create_reminder_tool,
    delete_reminder_tool,
    update_reminder_tool,
    list_reminders_tool,
    create_file_tool,
    update_file_tool,
    delete_file_tool,
    get_system_health_tool,
    get_connected_wifi_tool,
    get_available_wifi_tool,
    get_bluetooth_devices_tool,
    open_application_tool,
    close_application_tool,
)


class State(TypedDict):
    messages: Annotated[list, add_messages]

def should_tool_call(state: State):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return 'tools'
    return END

tool_node = ToolNode([
    create_reminder_tool,
    delete_reminder_tool,
    update_reminder_tool,
    list_reminders_tool,
    create_file_tool,
    update_file_tool,
    delete_file_tool,
    get_system_health_tool,
    get_connected_wifi_tool,
    get_available_wifi_tool,
    get_bluetooth_devices_tool,
    open_application_tool,
    close_application_tool,
])


workflow = StateGraph(State)

workflow.add_node('system_agent', call_system_llm)
workflow.add_node('tool_node', tool_node)
workflow.add_edge(START, 'system_agent')
workflow.add_conditional_edges(
    'system_agent',
    should_tool_call,
    {
        'tools': 'tool_node',
        END: END,
    },
)
workflow.add_edge('tool_node', 'system_agent')


system_graph = workflow.compile()

