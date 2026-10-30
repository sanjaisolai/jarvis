from winotify import Notification
import sys

title = sys.argv[1]

toast = Notification(
    app_id="Jarvis",
    title=title,
    msg="From Jarvis"
)

toast.show()