from tools.system.system_tool import (
    create_reminder as system_create_reminder,
    delete_reminder as system_delete_reminder,
    update_reminder as system_update_reminder,
    list_reminders as system_list_reminders,
    create_file as system_create_file,
    update_file as system_update_file,
    delete_file as system_delete_file,
    get_system_health as system_get_system_health,
    get_connected_wifi as system_get_connected_wifi,
    get_available_wifi as system_get_available_wifi,
    get_bluetooth_devices as system_get_bluetooth_devices,
    open_application as system_open_application,
    close_application as system_close_application,
)
from langchain_core.tools import tool

@tool
def create_reminder_tool(title: str, remind_at: str):
    """
        Create a Windows reminder.
    
        remind_at must be in:
        YYYY-MM-DD HH:MM
    
        Example:
        create_reminder(
            "Submit timesheet",
            "2026-08-24 18:00"
        )
        """
    return system_create_reminder(
        title=title,
        remind_at=remind_at,
    )


@tool
def delete_reminder_tool(task_name: str):
    """
        Delete a Jarvis Windows reminder.
    
        Example:
        delete_reminder("JarvisReminder_20260824180000")
    """
    return system_delete_reminder(task_name=task_name)


@tool
def update_reminder_tool(task_name: str, title: str, remind_at: str):
    """Update an existing Jarvis Windows reminder."""
    return system_update_reminder(
        task_name=task_name,
        title=title,
        remind_at=remind_at,
    )


@tool
def list_reminders_tool():
    """List all reminders created by Jarvis."""
    return system_list_reminders()


@tool
def create_file_tool(path: str, content: str = ""):
    """
        Create a file on the local Windows computer.
    
        Example:
        create_file(
            "C:/Users/Sanjai/Desktop/test.txt",
            "Hello from Jarvis"
        )
        """
    return system_create_file(
        path=path,
        content=content,
    )


@tool
def update_file_tool(path: str, content: str):
    """Replace the contents of an existing local file."""
    return system_update_file(
        path=path,
        content=content,
    )


@tool
def delete_file_tool(path: str):
    """Delete a local file."""
    return system_delete_file(path=path)


@tool
def get_system_health_tool():
    """
        Get current Windows system health information including
        CPU, memory, disk and uptime.
        """
    return system_get_system_health()


@tool
def get_connected_wifi_tool():
    """Get the currently connected Wi-Fi network."""
    return system_get_connected_wifi()


@tool
def get_available_wifi_tool():
    """Get nearby available Wi-Fi networks."""
    return system_get_available_wifi()


@tool
def get_bluetooth_devices_tool():
    """Get Bluetooth devices known to Windows."""
    return system_get_bluetooth_devices()


@tool
def open_application_tool(app_name: str):
    """Open an allowed Windows application."""
    return system_open_application(app_name=app_name)


@tool
def close_application_tool(app_name: str):
    """Close an allowed Windows application."""
    return system_close_application(app_name=app_name)



