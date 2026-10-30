from langchain_core.tools import tool
from tools.communication.models import EmailThread
from tools.communication.utils import _parse_email_message
from tools.google_support.google_auth import get_gmail_service, get_calendar_service
import base64
import datetime
from email.mime.text import MIMEText
from memory.pinecone_service import search_memories
from googleapiclient.errors import HttpError


@tool
def search_emails(
    query: str = "",
    max_results: int = 5,
    after: str = "",
    before: str = ""
) -> str:
    """Search Gmail messages.

    Args:
        query: Gmail search query, e.g. 'from:someone subject:invoice'.
        max_results: Maximum number of messages to return.
        after: Optional date in YYYY-MM-DD format. Returns emails after this date.
        before: Optional date in YYYY-MM-DD format. Returns emails before this date.

    If no query is given, returns the most recent messages.
    """

    service = get_gmail_service()

    search_query = query.strip()

    if after:
        search_query += f" after:{after}"

    if before:
        search_query += f" before:{before}"

    list_kwargs = {
        "userId": "me",
        "maxResults": max_results
    }

    if search_query:
        list_kwargs["q"] = search_query

    results = service.users().messages().list(**list_kwargs).execute()
    messages = results.get("messages", [])

    if not messages:
        return "No messages found."

    output = []

    for m in messages:
        msg = service.users().messages().get(
            userId="me",
            id=m["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()

        headers = {
            h["name"]: h["value"]
            for h in msg["payload"]["headers"]
        }

        output.append(
            f"Message ID: {msg['id']}\n"
            f"Thread ID: {msg['threadId']}\n"
            f"From: {headers.get('From')}\n"
            f"Subject: {headers.get('Subject')}\n"
            f"Date: {headers.get('Date')}\n"
            f"Snippet: {msg.get('snippet', '')}\n"
        )

    return "\n---\n".join(output)

@tool
def get_email(message_id: str) -> dict:
    """Retrieve the complete contents of a Gmail message."""

    service = get_gmail_service()

    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full",
    ).execute()

    email = _parse_email_message(msg)

    return email.model_dump()


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail."""
    service = get_gmail_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return f"Email sent to {to}."

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
def get_thread(thread_id: str) -> dict:
    """
    Retrieve the complete Gmail conversation/thread.
    """

    service = get_gmail_service()

    try:
        thread = service.users().threads().get(
            userId="me",
            id=thread_id,
            format="full",
        ).execute()

    except HttpError as error:
        if error.resp.status != 404:
            raise

        message = service.users().messages().get(
            userId="me",
            id=thread_id,
            format="minimal",
        ).execute()

        resolved_thread_id = message.get("threadId")

        if not resolved_thread_id:
            raise

        thread = service.users().threads().get(
            userId="me",
            id=resolved_thread_id,
            format="full",
        ).execute()

    messages = thread.get("messages", [])

    if not messages:
        return {
            "thread_id": thread_id,
            "messages": [],
        }

    parsed_messages = [
        _parse_email_message(message)
        for message in messages
    ]

    return EmailThread(
        thread_id=thread.get("id", thread_id),
        messages=parsed_messages,
    ).model_dump()



@tool
def reply_to_email(
    thread_id: str,
    message_id: str,
    to: str,
    body: str,
) -> str:
    """

    Reply to an EXISTING Gmail conversation.

    ALWAYS use this tool when responding to an existing email.
    Do NOT use send_email for replies.

    body must contain ONLY the new reply text.
    Do not include previous conversation or quoted messages.

    thread_id:
        Gmail thread ID of the conversation.

    message_id:
        Gmail message ID of the message being replied to.

    to:
        Recipient email address.

    body:
        Reply body.

    The reply is sent inside the existing Gmail conversation.
    """

    service = get_gmail_service()

    # Retrieve the original message so we can obtain
    # the RFC Message-ID and subject.
    original = service.users().messages().get(
        userId="me",
        id=message_id,
        format="metadata",
        metadataHeaders=[
            "Message-ID",
            "Subject",
            "From",
            "To",
            "References",
        ],
    ).execute()

    headers = {
        h["name"].lower(): h["value"]
        for h in original.get("payload", {}).get("headers", [])
    }

    original_message_id = headers.get("message-id")
    subject = headers.get("subject", "")

    # Make sure the subject follows normal reply formatting.
    if subject and not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    message = MIMEText(body)

    message["To"] = to
    message["Subject"] = subject

    # Required for proper email threading.
    if original_message_id:
        message["In-Reply-To"] = original_message_id

        references = headers.get("references", "")

        if references:
            message["References"] = (
                f"{references} {original_message_id}"
            )
        else:
            message["References"] = original_message_id

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    sent_message = service.users().messages().send(
        userId="me",
        body={
            "raw": raw,
            "threadId": thread_id,
        },
    ).execute()

    return (
        f"Reply sent successfully to {to}. "
        f"Message ID: {sent_message.get('id')}. "
        f"Thread ID: {sent_message.get('threadId', thread_id)}."
    )


@tool
def search_memories_tool(query: str, top_k: int = 5):
    """
    Search the user's long-term memory for relevant personal context.

    Use when communication tasks require information not available
    in the current conversation or email thread, such as:
    - Communication preferences
    - Writing style or tone
    - Relationships with recipients
    - Preferences for specific people
    - Relevant past decisions or context

    Do not use for general knowledge or information already available
    in the current conversation.

    Args:
        query: Semantic query describing the user information needed.
        top_k: Number of relevant memories to retrieve.
               Increase up to 10 if results are insufficient.
    """

    return search_memories(
        user_id="user_123",
        query=query,
        top_k=top_k
    )

