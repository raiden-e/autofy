import config
from telethon import TelegramClient, events, sync

from .telegram import get_telegram_client


def sendfail(msg):
    try:
        with get_telegram_client as client:
            print("sending message")
            client.send_message('me', str(msg))
    except Exception:
        with TelegramClient('Raiden', config.TELEID, config.TELEHASH) as client:
            client.send_message('me', str(msg))
