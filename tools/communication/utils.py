import base64
from tools.communication.models import EmailAttachment, EmailMessage

def _decode_body(data: str) -> str:
    return base64.urlsafe_b64decode(data).decode(
        "utf-8",
        errors="replace",
    )


def _extract_email_content(payload: dict) -> tuple[str | None, str | None]:
    """
    Extract both plain-text and HTML content from a Gmail payload.
    """

    text_body = None
    html_body = None

    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    if body_data:
        decoded = _decode_body(body_data)

        if mime_type == "text/plain":
            text_body = decoded

        elif mime_type == "text/html":
            html_body = decoded

    for part in payload.get("parts", []):
        part_text, part_html = _extract_email_content(part)

        if part_text and not text_body:
            text_body = part_text

        if part_html and not html_body:
            html_body = part_html

    return text_body, html_body

def _extract_attachments(payload: dict) -> list[EmailAttachment]:
    attachments = []

    mime_type = payload.get("mimeType", "")
    filename = payload.get("filename", "")
    body = payload.get("body", {})

    if filename:
        attachments.append(
            EmailAttachment(
                id=payload.get("partId", ""),
                filename=filename,
                mime_type=mime_type,
                size=body.get("size", 0),
                attachment_id=body.get("attachmentId"),
                inline=mime_type.startswith("image/"),
                content_id=next(
                    (
                        h["value"]
                        for h in payload.get("headers", [])
                        if h["name"].lower() == "content-id"
                    ),
                    None,
                ),
            )
        )

    for part in payload.get("parts", []):
        attachments.extend(
            _extract_attachments(part)
        )

    return attachments



def _split_addresses(value: str) -> list[str]:
    if not value:
        return []

    return [
        address.strip()
        for address in value.split(",")
        if address.strip()
    ]



def _parse_email_message(msg: dict) -> EmailMessage:
    payload = msg.get("payload", {})

    headers = {
        h["name"].lower(): h["value"]
        for h in payload.get("headers", [])
    }

    text_body, html_body = _extract_email_content(payload)

    attachments = _extract_attachments(payload)

    return EmailMessage(
        id=msg["id"],
        thread_id=msg["threadId"],

        sender=headers.get("from", ""),
        recipients=_split_addresses(headers.get("to", "")),
        cc=_split_addresses(headers.get("cc", "")),
        bcc=_split_addresses(headers.get("bcc", "")),

        subject=headers.get("subject", ""),
        date=headers.get("date", ""),

        text_body=text_body,
        html_body=html_body,

        attachments=attachments,
    )