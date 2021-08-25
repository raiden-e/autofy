from telethon import TelegramClient, events, sync
from telethon.sessions import StringSession

try:
    import config
except ImportError:
    raise ImportError("Please make sure you rename config_template.py to config.py")


def send_main(msg):
    try:
        with get_telegram_client as client:
            print("sending message")
            client.send_message('me', str(msg))
    except Exception as e:
        print(f"Caught:\n{e}")
        with TelegramClient('Raiden', config.TELEID, config.TELEHASH) as client:
            client.send_message('me', str(msg))


def get_telegram_client():
    try:
        with TelegramClient(StringSession(config.TELEST), config.TELEID, config.TELEHASH) as client:
            return client
    except Exception:
        try:
            with TelegramClient('Raiden', config.TELEID, config.TELEHASH) as client:
                return client
        except Exception:
            raise ImportError(
                "Couldn't initialize client, did you set ur TELEST in config.py?")


if __name__ == "__main__":
    get_telegram_client()
