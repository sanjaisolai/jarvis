from langchain_core.tools import tool

from ui.models import (
    UIComponent,
    UICreateEvent,
    UIUpdateEvent,
    UIRemoveEvent,
    UIClearEvent,
)

from ui.manager import ui_manager



@tool
def create_ui(component: UIComponent) -> dict:
    """
    Create a new UI component on the user's screen.

    Always provide the complete UIComponent including:
    id, type, props, and layout.
    """

    ui_manager.create(component)

    return UICreateEvent(
        component=component
    ).model_dump()


@tool
def update_ui(component: UIComponent) -> dict:
    """
    Replace an existing UI component.

    Always provide the COMPLETE component state,
    including id, type, props, and layout.
    """

    ui_manager.update(component)

    return UIUpdateEvent(
        component=component
    ).model_dump()


@tool
def remove_ui(component_id: str) -> dict:
    """
    Remove a specific UI component from the screen.
    """

    ui_manager.remove(component_id)

    return UIRemoveEvent(
        id=component_id
    ).model_dump()


@tool
def clear_ui() -> dict:
    """
    Remove all dynamic UI components.
    """

    ui_manager.clear()

    return UIClearEvent().model_dump()

def get_ui_state():
    """
    Get the current UI components displayed on the user's screen.
    """

    return ui_manager.get_all()