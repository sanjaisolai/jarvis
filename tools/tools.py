from email.mime.text import MIMEText
import base64
from tools.web_search.tavily import web_search
# from web_search.tavily import web_search
from langchain_core.tools import tool
from tools.google_support.google_auth import get_calendar_service
# from google_support.google_auth import get_gmail_service, get_calendar_service
from typing import Literal
from memory.pinecone_service import search_memories
import datetime
from graph.system_agent_graph import system_graph
from graph.ui_agent_graph import ui_graph
from typing import Any
from graph.communication_agent_graph import communication_graph
@tool
def web_search_tool(query: str,
    time_range: Literal["day", "week", "month", "year"] | None = None,
    topic: Literal["news", "general"] | None = None,) -> dict:
    """
    Search the web for current or general information.

    Use this tool when the user's question requires information
    that may be current, recent, or needs web verification.

    Args:
        query:
            A clear Google-style search query.

        topic:
            Search category. Must be one of:
            - "news": current events, breaking news, weather,
              sports, finance, announcements.
            - "general": documentation, programming, tutorials,
              comparisons, biographies, historical facts.

        time_range:
            Restrict results to a recent period. Must be one of:
            - "day"
            - "week"
            - "month"
            - "year"

            Prefer "day" for latest/current news or updates.
            Use "week" or longer when appropriate.
    """
    return web_search(query, time_range=time_range, topic=topic)

# @tool
# def search_emails(query: str = "", max_results: int = 5) -> str:
#     """Search Gmail messages. Use Gmail search syntax, e.g. 'from:someone subject:invoice'.
#     If no query is given, returns the most recent messages."""
#     service = get_gmail_service()

#     list_kwargs = {"userId": "me", "maxResults": max_results}
#     if query:
#         list_kwargs["q"] = query

#     results = service.users().messages().list(**list_kwargs).execute()
#     messages = results.get("messages", [])

#     if not messages:
#         return "No messages found."

#     output = []
#     for m in messages:
#         msg = service.users().messages().get(
#             userId="me", id=m["id"], format="metadata",
#             metadataHeaders=["Subject", "From", "Date"]
#         ).execute()
#         headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
#         snippet = msg.get("snippet", "")
#         output.append(
#             f"From: {headers.get('From')}\nSubject: {headers.get('Subject')}\n"
#             f"Date: {headers.get('Date')}\nSnippet: {snippet}\n"
#         )
#     return "\n---\n".join(output)


# @tool
# def send_email(to: str, subject: str, body: str) -> str:
#     """Send an email via Gmail."""
#     service = get_gmail_service()
#     message = MIMEText(body)
#     message["to"] = to
#     message["subject"] = subject
#     raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
#     service.users().messages().send(userId="me", body={"raw": raw}).execute()
#     return f"Email sent to {to}."


@tool
def list_calendar_events(max_results: int = 10, date: str = "") -> str:
    """List upcoming Google Calendar events.
    date is optional, format 'YYYY-MM-DD'. If given, lists events for that specific day only.
    If omitted, lists the next upcoming events from now."""
    service = get_calendar_service()

    if date:
        day_start = datetime.datetime.fromisoformat(date + "T00:00:00").isoformat() + "Z"
        day_end = datetime.datetime.fromisoformat(date + "T23:59:59").isoformat() + "Z"
        time_min, time_max = day_start, day_end
    else:
        time_min = datetime.datetime.utcnow().isoformat() + "Z"
        time_max = None

    list_kwargs = {
        "calendarId": "primary",
        "timeMin": time_min,
        "maxResults": max_results,
        "singleEvents": True,
        "orderBy": "startTime",
    }
    if time_max:
        list_kwargs["timeMax"] = time_max

    events_result = service.events().list(**list_kwargs).execute()
    events = events_result.get("items", [])

    if not events:
        return "No events found."

    output = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        output.append(f"{e['id']} | {start} - {e.get('summary', '(no title)')}")
    return "\n".join(output)


@tool
def create_calendar_event(summary: str, start: str, end: str, attendees: str = "") -> str:
    """Create a Google Calendar event. start/end must be ISO datetime, e.g. '2026-08-25T15:00:00+05:30'.
    attendees is a comma-separated list of emails (optional)."""
    service = get_calendar_service()
    event_body = {
        "summary": summary,
        "start": {"dateTime": start},
        "end": {"dateTime": end},
    }
    if attendees:
        event_body["attendees"] = [{"email": e.strip()} for e in attendees.split(",")]

    event = service.events().insert(calendarId="primary", body=event_body).execute()
    return f"Event created: {event.get('htmlLink')}"

@tool
def delete_calendar_event(event_id: str) -> str:
    """Delete/cancel a calendar event by its event ID.
    Use list_calendar_events first to find the event ID of the event to cancel."""
    service = get_calendar_service()
    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return f"Event {event_id} deleted."
    except Exception as e:
        return f"Failed to delete event {event_id}: {e}"


@tool
def search_memories_tool(query: str, top_k: int = 5):
    """
    Search the user's long-term memory.

    Use when you need information about the user from previous
    conversations, such as preferences, skills, projects, goals,
    or past decisions.

    Do not use for general knowledge or information already in
    the current conversation.

    The query should describe what user information you need.
    Example 1: "What programming languages does the user prefer?"
    Example 2: "Countries prefered by the user to travel"

    Args:
        query: Semantic query describing the user information needed.
        top_k: Number of relevant memories to retrieve.(Increase this number to max 10 if no relevant information is found)
    """
    print('memory called', query, "user_123", top_k)
    x = search_memories(user_id="user_123", query=query, top_k=top_k)
    print('memory result', x)
    return x



#------------------System tools--------------------
@tool
async def system_subagent_tool(messages: str):
    """
    Specialized sub-agent for executing local system operations.

    Use this tool when the user requests actions on the local
    Windows computer, such as managing reminders, files, system
    health, Wi-Fi networks, Bluetooth devices, or applications.

    The tool will handle the requested operations and return
    the results. Do not attempt to perform these actions directly.
    """
    
    state = {
        "messages": [{
            "role": "user",
            "content": messages
        }]
    }
    result = await system_graph.ainvoke(state)
    return result["messages"][-1].content



@tool
async def ui_subagent_tool(
    request: str,
    content: dict[str, Any],
):
    """
    Delegate UI presentation to the UI sub-agent.

    Use this when content needs to be displayed,
    formatted, positioned, resized, or updated
    in Jarvis's dynamic UI.

    The caller is responsible for fetching the
    actual content. This sub-agent only decides
    how that content should be represented in the UI.
    """

    state = {
        "messages": [
            {
                "role": "user",
                "content": f"""
                    UI REQUEST:
                    {request}

                    CONTENT TO DISPLAY:
                    {content}
                """
            }
        ]
    }

    result = await ui_graph.ainvoke(state)

    return result["messages"][-1].content



@tool
async def communication_subagent_tool(query: str, context: dict[str, Any] | None = None):
    """
    Delegate communication-related tasks to Jarvis's Communication Agent.

    Use this tool when the user wants to:
    - Read, search, or summarize emails.
    - Understand an email or conversation.
    - Draft, rewrite, or reply to an email.
    - Send or forward emails.
    - Find emails requiring attention or follow-up.
    - Extract requests, deadlines, or commitments from emails.
    - Check calendar events related to communication.
    - Create or manage calendar events.
    - Perform multi-step email/calendar workflows.

    Provide the Communication Agent with the user's complete request
    and any relevant context available from the current conversation.

    Do not use this tool for general questions or tasks unrelated to
    email, communication, or calendar management.

    The Communication Agent will determine which communication tools
    are required and execute the task safely.

    Args:
        query: The user's communication request and relevant context.
        context: Additional context for the communication request.
    """
    context_text = ""

    if context:
        context_text = f"""

    RELEVANT CONTEXT:
    {context}
    """

    state = {
                "messages": [{
                        "role": "user",
                        "content": f"""
                    USER REQUEST:
                    {query}
                    {context_text}
                """
                }]
            }

    result = await communication_graph.ainvoke(state)

    return result["messages"][-1].content


 


