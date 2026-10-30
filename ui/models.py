from typing import Annotated, Literal

from pydantic import BaseModel, Field


# ============================================================
# LAYOUT
# ============================================================

PresetPosition = Literal[
    "top-left",
    "top-center",
    "top-right",
    "center-left",
    "center",
    "center-right",
    "bottom-left",
    "bottom-center",
    "bottom-right",
]


class StandardLayout(BaseModel):
    position: PresetPosition

    width: int = Field(gt=0)
    height: int = Field(gt=0)

    zIndex: int = 10
    visible: bool = True


class CustomLayout(BaseModel):
    position: Literal["custom"]

    x: int
    y: int

    width: int = Field(gt=0)
    height: int = Field(gt=0)

    zIndex: int = 10
    visible: bool = True


UILayout = StandardLayout | CustomLayout


# ============================================================
# TEXT
# ============================================================

class TextProps(BaseModel):

    text: str = Field(
        default="",
        description=(
            "HTML string to render inside the text component. "
            "Use HTML tags for formatting such as "
            "<p>, <br>, <strong>, <em>, <ul>, <ol>, and <li>. "
            "Do not return Markdown. "
            "Do not use literal '\\n' characters for visual line breaks. "
            "Return valid HTML as a string."
        ),
    )


class TextComponent(BaseModel):
    id: str
    type: Literal["text"]
    props: TextProps
    layout: UILayout


# ============================================================
# NEWS
# ============================================================

class Article(BaseModel):
    title: str
    description: str | None = None
    url: str | None = None
    image: str | None = None


class NewsProps(BaseModel):
    title: str = "News"
    articles: list[Article] = Field(
        min_length=1,
    )


class NewsComponent(BaseModel):
    id: str
    type: Literal["news"]
    props: NewsProps
    layout: UILayout


# ============================================================
# VIDEO
# ============================================================

class VideoProps(BaseModel):
    title: str = "Video"
    url: str | None = None


class VideoComponent(BaseModel):
    id: str
    type: Literal["video"]
    props: VideoProps
    layout: UILayout


# # ============================================================
# # IMAGE
# # ============================================================

# class ImageProps(BaseModel):
#     url: str
#     title: str | None = None


# class ImageComponent(BaseModel):
#     id: str
#     type: Literal["image"]
#     props: ImageProps
#     layout: UILayout


# # ============================================================
# # CARD
# # ============================================================

# class CardProps(BaseModel):
#     title: str | None = None
#     content: str | None = None


# class CardComponent(BaseModel):
#     id: str
#     type: Literal["card"]
#     props: CardProps
#     layout: UILayout


# # ============================================================
# # LIST
# # ============================================================

# class ListProps(BaseModel):
#     title: str | None = None
#     items: list[str] = Field(
#         default_factory=list
#     )


# class ListComponent(BaseModel):
#     id: str
#     type: Literal["list"]
#     props: ListProps
#     layout: UILayout


# ============================================================
# UI COMPONENT
# ============================================================

UIComponent = Annotated[
    (
        TextComponent
        | NewsComponent
        | VideoComponent
    ),
    Field(discriminator="type"),
]


# ============================================================
# UI EVENTS
# ============================================================

class UICreateEvent(BaseModel):
    type: Literal["ui.create"] = "ui.create"
    component: UIComponent


class UIUpdateEvent(BaseModel):
    type: Literal["ui.update"] = "ui.update"
    component: UIComponent


class UIRemoveEvent(BaseModel):
    type: Literal["ui.remove"] = "ui.remove"
    id: str


class UIClearEvent(BaseModel):
    type: Literal["ui.clear"] = "ui.clear"