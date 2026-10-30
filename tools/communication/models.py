from pydantic import BaseModel, Field
from typing import Optional


class EmailAttachment(BaseModel):
    id: str
    filename: str
    mime_type: str
    size: int = 0
    attachment_id: Optional[str] = None
    inline: bool = False
    content_id: Optional[str] = None


class EmailMessage(BaseModel):
    id: str
    thread_id: str

    sender: str
    recipients: list[str] = Field(default_factory=list)
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)

    subject: str
    date: str

    text_body: Optional[str] = None
    html_body: Optional[str] = None

    attachments: list[EmailAttachment] = Field(default_factory=list)


class EmailThread(BaseModel):
    thread_id: str
    messages: list[EmailMessage]