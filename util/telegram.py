import config
from telethon import TelegramClient
from telethon.sessions import StringSession


def send_main(msg):
    try:
        client = get_telegram_client()
        print("sending message")
        client.send_message('me', str(msg))
    except Exception as e:
        print(f"Caught:\n{e}")
        with TelegramClient('Raiden', config.TELEGRAM['ID'], config.TELEGRAM['HASH']) as client:
            client.send_message('me', str(msg))


def get_telegram_client():
    try:
        with TelegramClient(StringSession(config.TELEGRAM['CACHE']), config.TELEGRAM['ID'], config.TELEGRAM['HASH']) as client:
            return client
    except Exception:
        with TelegramClient('Raiden', config.TELEGRAM['ID'], config.TELEGRAM['HASH']) as client:
            return client


if __name__ == "__main__":
    get_telegram_client()
