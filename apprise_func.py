import apprise
from dotenv import load_dotenv
import os

load_dotenv()


# Create an Apprise instance
def telegram_notify(title, body):
    token = os.environ.get("APPRISE_TOKEN")
    target_num = os.environ.get("APPRISE_TARGET")
    target = f"tgram://{token}/{target_num}"

    apobj = apprise.Apprise()
    apobj.add(target)

    apobj.notify(
        body=body,
        title=title,
    )
