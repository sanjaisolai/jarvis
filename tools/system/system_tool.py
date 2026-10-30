import os
import subprocess
import sys
import psutil

from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool


# ============================================================
# Helpers
# ============================================================

def run_powershell(command: str):
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    final_result = result.stdout.strip()
    print(f"[run_powershell] Result: {final_result}")
    return final_result


# ============================================================
# WINDOWS REMINDERS
# ============================================================

def create_reminder(
    title: str,
    remind_at: str,
):
    """
    Create a Windows reminder.

    remind_at:
        YYYY-MM-DD HH:MM
    """

    print("remind_at:", remind_at)

    dt = datetime.strptime(remind_at, "%Y-%m-%d %H:%M")

    task_name = f"JarvisReminder_{dt.strftime('%Y%m%d%H%M%S')}"

    # ---------------------------------------------------------
    # Python reminder script
    # ---------------------------------------------------------

    python_exe = sys.executable
    reminder_script = Path(__file__).with_name("show_reminder.py")

    script_path = str(reminder_script).replace("'", "''")
    safe_title = title.replace("'", "''")

    # ---------------------------------------------------------
    # PowerShell command used ONLY to create the task
    # ---------------------------------------------------------

    command = f"""
$action = New-ScheduledTaskAction `
    -Execute "{python_exe}" `
    -Argument '"{script_path}" -Title "{safe_title}"'

$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At ([datetime]"{dt.strftime("%Y-%m-%d %H:%M:%S")}")

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName "{task_name}" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Force
"""

    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        capture_output=True,
        text=True,
    )

    print(f"[create_reminder] Result: {result}")

    if result.returncode != 0:
        response = (
            f"Failed to create reminder: "
            f"{result.stderr.strip()}"
        )
        print(f"[create_reminder] Result: {response}")
        return response

    response = f"Reminder '{title}' created for {remind_at}."
    print(f"[create_reminder] Result: {response}")

    return response



def delete_reminder(task_name: str):
    """
    Delete a Jarvis Windows reminder.

    Example:
    delete_reminder("JarvisReminder_20260824180000")
    """

    result = subprocess.run(
        [
            "schtasks",
            "/Delete",
            "/TN",
            task_name,
            "/F",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        response = f"Failed to delete reminder: {result.stderr}"
        print(f"[delete_reminder] Result: {response}")
        return response

    response = f"Reminder {task_name} deleted."
    print(f"[delete_reminder] Result: {response}")
    return response



def update_reminder(
    task_name: str,
    title: str,
    remind_at: str,
):
    """
    Update an existing Jarvis reminder.
    """

    delete_result = delete_reminder(task_name=task_name)

    if "Failed" in delete_result:
        print(f"[update_reminder] Result: {delete_result}")
        return delete_result

    response = create_reminder(
        title=title,
        remind_at=remind_at,
    )
    print(f"[update_reminder] Result: {response}")
    return response



def list_reminders():
    """
    List all reminders created by Jarvis.
    """

    result = subprocess.run(
        [
            "schtasks",
            "/Query",
            "/FO",
            "LIST",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"[list_reminders] Result: {result.stderr}")
        return result.stderr

    lines = result.stdout.splitlines()

    reminders = []

    current = {}

    for line in lines:

        if line.startswith("TaskName:"):
            if current:
                reminders.append(current)

            current = {
                "task": line.split(":", 1)[1].strip()
            }

        elif line.startswith("Status:"):
            current["status"] = line.split(":", 1)[1].strip()

        elif line.startswith("Next Run Time:"):
            current["next_run"] = line.split(":", 1)[1].strip()

    if current:
        reminders.append(current)

    jarvis_reminders = [
        r for r in reminders
        if "JarvisReminder_" in r.get("task", "")
    ]

    print(f"[list_reminders] Result: {jarvis_reminders}")
    return jarvis_reminders


# ============================================================
# FILE OPERATIONS
# ============================================================


def create_file(
    path: str,
    content: str = "",
):
    """
    Create a file on the local Windows computer.

    Example:
    create_file(
        "C:/Users/Sanjai/Desktop/test.txt",
        "Hello from Jarvis"
    )
    """

    file_path = Path(path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if file_path.exists():
        response = f"File already exists: {path}"
        print(f"[create_file] Result: {response}")
        return response

    file_path.write_text(
        content,
        encoding="utf-8"
    )

    response = f"File created: {path}"
    print(f"[create_file] Result: {response}")
    return response



def update_file(
    path: str,
    content: str,
):
    """
    Replace the contents of an existing file.
    """

    file_path = Path(path)

    if not file_path.exists():
        response = f"File does not exist: {path}"
        print(f"[update_file] Result: {response}")
        return response

    file_path.write_text(
        content,
        encoding="utf-8"
    )

    response = f"File updated: {path}"
    print(f"[update_file] Result: {response}")
    return response



def delete_file(path: str):
    """
    Delete a local file.
    """

    file_path = Path(path)

    if not file_path.exists():
        response = f"File does not exist: {path}"
        print(f"[delete_file] Result: {response}")
        return response

    file_path.unlink()

    response = f"File deleted: {path}"
    print(f"[delete_file] Result: {response}")
    return response


# ============================================================
# SYSTEM HEALTH
# ============================================================

def get_system_health():
    """
    Get current Windows system health information including
    CPU, memory, disk and uptime.
    """

    cpu = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()

    disk = psutil.disk_usage("C:\\")

    uptime_seconds = (
        datetime.now().timestamp()
        - psutil.boot_time()
    )

    uptime_hours = uptime_seconds / 3600

    result = {
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "memory_available_gb": round(
            memory.available / (1024 ** 3),
            2
        ),
        "disk_percent": disk.percent,
        "disk_free_gb": round(
            disk.free / (1024 ** 3),
            2
        ),
        "uptime_hours": round(
            uptime_hours,
            2
        ),
    }
    print(f"[get_system_health] Result: {result}")
    return result


# ============================================================
# WIFI
# ============================================================


def get_connected_wifi():
    """
    Get the currently connected Wi-Fi network.
    """

    result = subprocess.run(
        [
            "netsh",
            "wlan",
            "show",
            "interfaces"
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        response = result.stderr
        print(f"[get_connected_wifi] Result: {response}")
        return response

    for line in result.stdout.splitlines():

        line = line.strip()

        if line.startswith("SSID"):
            response = line.split(":", 1)[1].strip()
            print(f"[get_connected_wifi] Result: {response}")
            return response

    response = "No Wi-Fi connection found."
    print(f"[get_connected_wifi] Result: {response}")
    return response



def get_available_wifi():
    """
    Get nearby available Wi-Fi networks.
    """

    result = subprocess.run(
        [
            "netsh",
            "wlan",
            "show",
            "networks"
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        response = result.stderr
        print(f"[get_available_wifi] Result: {response}")
        return response

    networks = []

    for line in result.stdout.splitlines():

        line = line.strip()

        if line.startswith("SSID"):
            name = line.split(":", 1)[1].strip()

            if name:
                networks.append(name)

    response = list(dict.fromkeys(networks))
    print(f"[get_available_wifi] Result: {response}")
    return response


# ============================================================
# BLUETOOTH
# ============================================================



def get_bluetooth_devices():
    """
    Get Bluetooth devices known to Windows.
    """

    command = """
    Get-PnpDevice -Class Bluetooth |
    Select-Object Status, FriendlyName, InstanceId |
    ConvertTo-Json
    """

    try:
        output = run_powershell(command)

        if not output:
            print(f"[get_bluetooth_devices] Result: []")
            return []

        print(f"[get_bluetooth_devices] Result: {output}")
        return output

    except Exception as e:
        response = f"Bluetooth query failed: {e}"
        print(f"[get_bluetooth_devices] Result: {response}")
        return response


# ============================================================
# APPLICATION CONTROL
# ============================================================

# IMPORTANT:
# Keep an allowlist instead of allowing the LLM to execute
# arbitrary commands.

ALLOWED_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "edge": "msedge.exe",
    "vscode": "code.exe",
}



def open_application(app_name: str):
    """
    Open an allowed Windows application.

    Examples:
    open_application("chrome")
    open_application("notepad")
    open_application("vscode")
    """

    app_name = app_name.lower().strip()

    if app_name not in ALLOWED_APPS:
        response = (
            f"Application '{app_name}' is not allowed. "
            f"Allowed applications: "
            f"{', '.join(ALLOWED_APPS.keys())}"
        )
        print(f"[open_application] Result: {response}")
        return response

    command = ALLOWED_APPS[app_name]

    try:

        subprocess.Popen(
            command,
            shell=True
        )

        response = f"Opened {app_name}."
        print(f"[open_application] Result: {response}")
        return response

    except Exception as e:
        response = f"Failed to open {app_name}: {e}"
        print(f"[open_application] Result: {response}")
        return response


def close_application(app_name: str):
    """
    Close an allowed Windows application.
    """

    process_names = {
        "notepad": "notepad.exe",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "vscode": "Code.exe",
        "calculator": "CalculatorApp.exe",
    }

    app_name = app_name.lower().strip()

    if app_name not in process_names:
        response = (
            f"Application '{app_name}' is not allowed."
        )
        print(f"[close_application] Result: {response}")
        return response

    process = process_names[app_name]

    result = subprocess.run(
        [
            "taskkill",
            "/IM",
            process,
            "/F",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        response = (
            f"Could not close {app_name}: "
            f"{result.stderr.strip()}"
        )
        print(f"[close_application] Result: {response}")
        return response

    response = f"Closed {app_name}."
    print(f"[close_application] Result: {response}")
    return response