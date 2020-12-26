import config
from telethon import TelegramClient, events, sync
from telethon.sessions import StringSession


def get_telegram_client():
    try:
        with TelegramClient(StringSession(config.TELEST), config.TELEID, config.TELEHASH) as client:
            return client
    except Exception:
        raise "Couldnt initialize client, did you set ur telest in config.py?"


if __name__ == "__main__":
    get_telegram_client()
