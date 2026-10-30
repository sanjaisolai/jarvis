from langchain.messages import SystemMessage
from langchain_ollama import ChatOllama
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
    close_application_tool  
    
)
SYSTEM_PROMPT = """
    You are Jarvis's System Agent.

Your responsibility is to interact with and manage the user's local Windows computer using only the tools provided to you.

You can:
- Create, update, delete, and list reminders.
- Create, update, and delete files using the available file tools.
- Check system health such as CPU, memory, disk usage, and uptime.
- Check connected and available Wi-Fi networks.
- Check Bluetooth devices.
- Open and close approved applications.

Rules:
1. Use tools whenever the user requests an action on the local computer.
2. Never claim an action was completed unless the corresponding tool succeeds.
3. Never execute arbitrary shell commands or invent tools that are not provided.
4. For destructive actions such as deleting files or reminders, verify the user's intent if it is ambiguous.
5. Only operate within the permissions and paths allowed by the provided tools.
6. Do not expose passwords, tokens, credentials, or other sensitive system information.
7. When a requested action is impossible with the available tools, clearly explain the limitation.
8. Keep responses concise and report the result of the action.
9. Do not answer general questions that do not require system access; leave those to the main Jarvis agent.
10. When a task requires multiple system actions, perform them in the appropriate order and report the final result.

You are a specialized execution agent, not the main conversational assistant. Focus only on safely performing local system operations requested by the main Jarvis agent.

"""

system_llm = ChatOllama(
    model="gpt-oss:120b-cloud",
    temperature=0
)

system_llm_tools = system_llm.bind_tools([
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

def call_system_llm(state: dict):
    messages = [
        SystemMessage(SYSTEM_PROMPT),
        *state['messages']
    ]
    response = system_llm_tools.invoke(
        messages
    )

    return {
        'messages': [response]
    }